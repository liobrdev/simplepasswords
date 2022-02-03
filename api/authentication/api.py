import logging

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone

from knox.settings import CONSTANTS
from knox.views import LoginView, LogoutView

from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    PermissionDenied,
    Throttled,
    ValidationError,)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import (
    EmailVerificationToken, PhoneVerificationToken,
    TwoFactorAuthToken,)
from authentication.verification import (
    send_verification_email, send_verification_sms, check_verification_token,)
from authentication.serializers import (
    LoginSerializer, RegistrationSerializer, TwoFactorAuthSerializer,
    VerificationSerializer,)
from authentication.utils import AuthCommands
from users.exceptions import DuplicateEmail, DuplicateSuperUser
from utils import parse_request_metadata
from utils.exceptions import RequestError
from utils.throttling import throttle_command


logger = logging.getLogger(__name__)

User = get_user_model()

class LoginAPI(LoginView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        try:
            if throttle_command(
                AuthCommands.LOGIN, request.META['CLIENT_IP'], request,
            ):
                raise Throttled()

            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data

            if (
                user.tfa_is_enabled and user.phone_number and
                user.phone_number_is_verified
            ):
                tfa_token = TwoFactorAuthToken.objects.create(
                    user=user, expiry=timedelta(minutes=5),)

                data = dict(tfa_token=tfa_token[1])

                try:
                    PhoneVerificationToken.objects.filter(
                        user=user, expiry__gt=timezone.now(),
                    ).latest('expiry')
                except PhoneVerificationToken.DoesNotExist:
                    phone_token = PhoneVerificationToken.objects.create(
                        user=user, expiry=timedelta(minutes=5),)

                    if settings.DJANGO_ENV == 'test':
                        data = dict(data, security_code=phone_token[1])
                    else:
                        send_verification_sms(
                            user.phone_number.as_e164,
                            settings.TWILIO_PHONE_NUMBER, phone_token[1],)

                return Response(data, status=status.HTTP_201_CREATED)

            login(request, user)
            return super().post(request, format=None)
        except (AuthenticationFailed, PermissionDenied, Throttled) as e:
            raise e
        except ValidationError as e:
            if hasattr(e, 'detail') and isinstance(e.detail, dict):
                for value in e.detail.values():
                    if value in [
                        ['This field is required.'],
                        ['This field may not be blank.'],
                    ]:
                        logger.exception(
                            'Missing login data.', exc_info=e, extra={
                                'client_ip': request.META['CLIENT_IP'],
                                'command': AuthCommands.LOGIN,
                                'metadata': parse_request_metadata(request),
                            },)
                        break
            raise e
        except Exception as e:
            logger.exception('User login error.', exc_info=e, extra={
                'client_ip': request.META['CLIENT_IP'],
                'command': AuthCommands.LOGIN,
                'metadata': parse_request_metadata(request),
            })
            raise RequestError('User login error.')


class RegistrationAPI(LoginAPI):
    def post(self, request, format=None):
        try:
            if throttle_command(
                AuthCommands.REGISTER, request.META['CLIENT_IP'], request,
            ):
                raise Throttled()
            registration = RegistrationSerializer(data=request.data)
            registration.is_valid(raise_exception=True)
            data = registration.validated_data
            user = User.objects.create_user(**data)
            return super().post(request, format=None)
        except Throttled as e:
            raise e
        except ValidationError as e:
            if hasattr(e, 'detail') and isinstance(e.detail, dict):
                for value in e.detail.values():
                    if value in [
                        ['This field is required.'],
                        ['This field may not be blank.'],
                    ]:
                        logger.exception(
                            'Missing register data.', exc_info=e, extra={
                                'client_ip': request.META['CLIENT_IP'],
                                'command': AuthCommands.REGISTER,
                                'metadata': parse_request_metadata(request),
                            },)
                        break
            raise e
        except PermissionDenied as e:
            if (
                hasattr(e, 'detail') and
                'You have been temporarily locked out of this account' \
                in e.detail
            ):
                try:
                    user = User.objects.get(email=request.data['email'])
                    user.is_active = False
                    user.save(update_fields=['is_active', 'updated_at'])
                except Exception as err:
                    logger.exception(
                        'Attempted register w/ locked email, fail deactivate',
                        exc_info=err, extra={
                            'client_ip': request.META['CLIENT_IP'],
                            'command': AuthCommands.REGISTER,
                            'metadata': parse_request_metadata(request),
                        },)
            raise e
        except (DuplicateEmail, DuplicateSuperUser):
            raise PermissionDenied('Cannot create account with this email.')
        except Exception as e:
            logger.exception(
                'User registration error.', exc_info=e, extra={
                    'client_ip': request.META['CLIENT_IP'],
                    'command': AuthCommands.REGISTER,
                    'metadata': parse_request_metadata(request),
                },)
            raise RequestError('User registration error.')


class LogoutAPI(LogoutView):
    def post(self, request, format=None):
        try:
            auth_header = request.headers.get('Authorization')
            token_key = auth_header.split()[1][:CONSTANTS.TOKEN_KEY_LENGTH]
            token = request.user.auth_token_set.get(token_key=token_key)
            deleted = token.delete()
            if deleted != (1, { 'knox.AuthToken': 1 }):
                raise RuntimeError('Token was not deleted properly')
            request._auth.delete()
            user_logged_out.send(sender=request.user.__class__,
                                 request=request, user=request.user)
            logout(request)
        except Exception as e:
            logger.exception(
                'User logout error.', exc_info=e, extra={
                    'user': request.user.user_slug,
                    'client_ip': request.META['CLIENT_IP'],
                    'command': AuthCommands.LOGOUT,
                    'metadata': parse_request_metadata(request),
                },)
        finally:
            return Response(None, status=status.HTTP_204_NO_CONTENT)


class VerifyEmailAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            if throttle_command(
                AuthCommands.VERIFY_EMAIL, request.META['CLIENT_IP'], request,
            ):
                raise Throttled()
            try:
                token = EmailVerificationToken.objects.filter(
                    user=request.user, expiry__gt=timezone.now(),
                ).latest('expiry')
            except EmailVerificationToken.DoesNotExist:
                user = request.user
                token = EmailVerificationToken.objects.create(
                    user=user, expiry=timedelta(days=7),)
                send_verification_email(user.email, user.name, token[1])
        except Throttled as e:
            raise e
        except Exception as e:
            logger.exception(
                'Email verification error - GET', exc_info=e, extra={
                    'client_ip': request.META['CLIENT_IP'],
                    'command': AuthCommands.VERIFY_EMAIL,
                    'metadata': parse_request_metadata(request),
                },)
            raise RequestError()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def post(self, request, format=None):
        try:
            if throttle_command(
                AuthCommands.VERIFY_EMAIL, request.META['CLIENT_IP'], request,
            ):
                raise Throttled()

            user = request.user
            if user.email_is_verified:
                return Response(None, status=status.HTTP_204_NO_CONTENT)

            token_string = ''
            serializer = VerificationSerializer(data=request.data)
            if serializer.is_valid():
                token_string = serializer.validated_data['token']

            try:
                check_verification_token(
                    AuthCommands.VERIFY_EMAIL, request.user, token_string,)
            except:
                msg = "Oops, failed to verify your email address! " \
                    "Perhaps the email link is no longer valid."
                raise PermissionDenied(msg)

            user.email_is_verified = True
            user.save()
            user.email_verification_tokens.all().delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except (PermissionDenied, Throttled) as e:
            raise e
        except Exception as e:
            logger.exception(
                'Email verification error - POST', exc_info=e, extra={
                    'client_ip': request.META['CLIENT_IP'],
                    'command': AuthCommands.VERIFY_EMAIL,
                    'metadata': parse_request_metadata(request),
                },)
            raise RequestError()


class VerifyPhoneAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            if throttle_command(
                AuthCommands.VERIFY_PHONE, request.META['CLIENT_IP'], request,
            ):
                raise Throttled()

            user = request.user

            if not user.phone_number:
                raise APIException('No phone number to verify.', code=400)

            try:
                token = PhoneVerificationToken.objects.filter(
                    user=user, expiry__gt=timezone.now(),
                ).latest('expiry')
            except PhoneVerificationToken.DoesNotExist:
                token = PhoneVerificationToken.objects.create(
                    user=user, expiry=timedelta(minutes=10),)

                if settings.DJANGO_ENV == 'test':
                    data = dict(token_string=token[1])
                    return Response(data, status=status.HTTP_204_NO_CONTENT)
                else:
                    send_verification_sms(
                        user.phone_number.as_e164,
                        settings.TWILIO_PHONE_NUMBER, token[1],)

            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except Throttled as e:
            raise e
        except Exception as e:
            logger.exception(
                'Phone verification error - GET', exc_info=e, extra={
                    'client_ip': request.META['CLIENT_IP'],
                    'command': AuthCommands.VERIFY_PHONE,
                    'metadata': parse_request_metadata(request),
                },)
            raise RequestError()

    def post(self, request, format=None):
        try:
            if throttle_command(
                AuthCommands.VERIFY_PHONE, request.META['CLIENT_IP'], request,
            ):
                raise Throttled()

            user = request.user

            if user.phone_number_is_verified:
                return Response(None, status=status.HTTP_204_NO_CONTENT)

            token_string = ''
            serializer = VerificationSerializer(data=request.data)

            if serializer.is_valid():
                token_string = serializer.validated_data['token']

            try:
                check_verification_token(
                    AuthCommands.VERIFY_PHONE, request.user, token_string,)
            except:
                msg = "Oops, failed to verify your phone number! " \
                    "Perhaps the security code is no longer valid."
                raise PermissionDenied(msg)

            user.phone_number_is_verified = True
            user.save()
            user.phone_verification_tokens.all().delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except (PermissionDenied, Throttled) as e:
            raise e
        except Exception as e:
            logger.exception(
                'Phone verification error - POST', exc_info=e, extra={
                    'client_ip': request.META['CLIENT_IP'],
                    'command': AuthCommands.VERIFY_PHONE,
                    'metadata': parse_request_metadata(request),
                    },)
            raise RequestError()


class TwoFactorAuthAPI(LoginView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        try:
            if throttle_command(
                AuthCommands.TFA, request.META['CLIENT_IP'], request,
            ):
                raise Throttled()
            
            serializer = TwoFactorAuthSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data
            user.tfa_tokens.all().delete()
            user.phone_verification_tokens.all().delete()
            login(request, user)

            return super().post(request, format=None)
        except (Throttled, ValidationError) as e:
            raise e
        except Exception as e:
            logger.exception('Two factor auth error.', exc_info=e, extra={
                'client_ip': request.META['CLIENT_IP'],
                'command': AuthCommands.TFA,
                'metadata': parse_request_metadata(request),
            })
            raise RequestError('Two-factor authentication error.')