import logging

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import status
from rest_framework.exceptions import Throttled, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from reset_password.models import (
    ResetPasswordEmailToken, ResetPasswordPhoneToken,
    ResetPasswordSubmitToken,)
from reset_password.utils import (
    send_reset_password_email, send_reset_password_sms, RPWCommands,)
from reset_password.serializers import (
    ResetPasswordRequestSerializer, ResetPasswordEmailSerializer,
    ResetPasswordPhoneSerializer,)
from utils import parse_request_metadata
from utils.exceptions import RequestError
from utils.throttling import throttle_command


logger = logging.getLogger(__name__)

User = get_user_model()

class ResetPasswordRequestAPI(APIView):
    def post(self, request, format=None):
        try:
            if throttle_command(
                RPWCommands.RPW_REQUEST, request.META['CLIENT_IP'], request,
            ):
                raise Throttled()

            serializer = ResetPasswordRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

            if not user or not user.is_active or not user.email_is_verified:
                return Response(None, status=status.HTTP_204_NO_CONTENT)

            try:
                ResetPasswordEmailToken.objects.get(
                    email=email, expiry__gt=timezone.now(),)
            except ResetPasswordEmailToken.DoesNotExist:
                token = ResetPasswordEmailToken.objects.create(
                    email=email, expiry=timedelta(hours=1),)
                user_agent = request.user_agent
                device_name = user_agent.device.family
                browser_name = (
                    f'{user_agent.browser.family} '
                    f'{user_agent.browser.version_string}')
                send_reset_password_email(
                    email, token[1], device_name, browser_name,)
        except (Throttled, ValidationError) as e:
            raise e
        except Exception as e:
            logger.exception('Error reset_password_request', exc_info=e, extra={
                'client_ip': request.META['CLIENT_IP'],
                'command': RPWCommands.RPW_REQUEST,
                'metadata': parse_request_metadata(request),
            })
            raise RequestError()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class ResetPasswordEmailAPI(APIView):
    def post(self, request, format=None):
        try:
            if throttle_command(
                RPWCommands.RPW_EMAIL, request.META['CLIENT_IP'], request,
            ):
                raise Throttled()

            serializer = ResetPasswordEmailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

            if (
                not user or not user.is_active or
                not user.phone_number or
                not user.phone_number_is_verified
            ):
                return Response(None, status=status.HTTP_204_NO_CONTENT)

            try:
                ResetPasswordPhoneToken.objects.get(
                    email=email, expiry__gt=timezone.now(),)
            except ResetPasswordPhoneToken.DoesNotExist:
                token = ResetPasswordPhoneToken.objects.create(
                    email=email, expiry=timedelta(minutes=10),)

                if settings.DJANGO_ENV == 'test':
                    data = dict(token_string=token[1])
                    return Response(data, status=status.HTTP_204_NO_CONTENT)
                else:
                    send_reset_password_sms(
                        user.phone_number.as_e164,
                        settings.TWILIO_PHONE_NUMBER, token[1],)
        except (Throttled, ValidationError) as e:
            raise e
        except Exception as e:
            logger.exception('Error reset_password_email', exc_info=e, extra={
                'client_ip': request.META['CLIENT_IP'],
                'command': RPWCommands.RPW_EMAIL,
                'metadata': parse_request_metadata(request),
            })
            raise RequestError()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class ResetPasswordPhoneAPI(APIView):
    def post(self, request, format=None):
        try:
            if throttle_command(
                RPWCommands.RPW_PHONE, request.META['CLIENT_IP'], request,
            ):
                raise Throttled()

            serializer = ResetPasswordPhoneSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data

            try:
                ResetPasswordSubmitToken.objects.get(
                    email=email, expiry__gt=timezone.now(),)
            except ResetPasswordSubmitToken.DoesNotExist:
                token = ResetPasswordSubmitToken.objects.create(
                    email=email, expiry=timedelta(minutes=5),)
                return Response(dict(token=token[1]))
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except (Throttled, ValidationError) as e:
            raise e
        except Exception as e:
            logger.exception('Error reset_password_phone', exc_info=e, extra={
                'client_ip': request.META['CLIENT_IP'],
                'command': RPWCommands.RPW_PHONE,
                'metadata': parse_request_metadata(request),
            })
            raise RequestError()