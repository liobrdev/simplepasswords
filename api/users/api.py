import logging

from rest_framework import status
from rest_framework.exceptions import (
    PermissionDenied,
    Throttled,
    ValidationError,)
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers import UserSerializer, UserDeactivateSerializer
from users.utils import UserCommands
from utils import parse_request_metadata
from utils.exceptions import RequestError
from utils.throttling import throttle_command

logger = logging.getLogger(__name__)


class UserAPI(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    lookup_field = 'user_slug'

    def get_object(self):
        user_slug = self.kwargs['user_slug']
        if self.request.user.user_slug == user_slug:
            return self.request.user
        raise PermissionDenied('User denied access.')

    def retrieve(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        headers = {
            'Access-Control-Expose-Headers': 'X-Client-Ip',
            'X-Client-Ip': request.META['CLIENT_IP'],
        }
        return Response(serializer.data, headers=headers)

    def destroy(self, request, *args, **kwargs):
        try:
            if throttle_command(
                UserCommands.DEACTIVATE, request.META['CLIENT_IP'], request,
            ):
                raise Throttled()
            serializer = UserDeactivateSerializer(
                data=request.data, context={ 'request': request },)
            serializer.is_valid(raise_exception=True)
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            raise e
        except PermissionDenied as e:
            logger.exception('User denied access.', exc_info=e, extra={
                'user': request.user.user_slug,
                'command': UserCommands.DEACTIVATE,
                'client_ip': request.META['CLIENT_IP'],
                'metadata': parse_request_metadata(request),
            })
            raise e
        except Exception as e:
            logger.exception('Error destroying user.', exc_info=e, extra={
                'user': request.user.user_slug,
                'command': UserCommands.DEACTIVATE,
                'client_ip': request.META['CLIENT_IP'],
                'metadata': parse_request_metadata(request),
            })
            raise RequestError('Error deactivating account.')

    def update(self, request, *args, **kwargs):
        try:
            if throttle_command(
                UserCommands.UPDATE, request.META['CLIENT_IP'], request,
            ):
                raise Throttled()
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            if hasattr(e, 'detail') and isinstance(e.detail, dict):
                for key, value in e.detail.items():
                    if value == ['This field may not be blank.']:
                        logger.exception('Blank user update.', exc_info=e, extra={
                            'user': request.user.user_slug,
                            'command': UserCommands.UPDATE,
                            'client_ip': request.META['CLIENT_IP'],
                            'metadata': parse_request_metadata(request),
                        })
                        break
                    if key == 'password' and value == [
                        'This password is too short. '
                        'It must contain at least 8 characters.',
                    ]:
                        logger.exception('Short password.', exc_info=e, extra={
                            'user': request.user.user_slug,
                            'command': UserCommands.UPDATE,
                            'client_ip': request.META['CLIENT_IP'],
                            'metadata': parse_request_metadata(request),
                        })
                        break
            raise e
        except PermissionDenied as e:
            logger.exception('User denied access.', exc_info=e, extra={
                'user': request.user.user_slug,
                'command': UserCommands.UPDATE,
                'client_ip': request.META['CLIENT_IP'],
                'metadata': parse_request_metadata(request),
            })
            raise e
        except Exception as e:
            logger.exception('Error updating user.', exc_info=e, extra={
                'user': request.user.user_slug,
                'command': UserCommands.UPDATE,
                'client_ip': request.META['CLIENT_IP'],
                'metadata': parse_request_metadata(request),
            })
            raise RequestError('Error updating account.')

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.auth_token_set.all().delete()
        instance.email_verification_tokens.all().delete()
        instance.phone_verification_tokens.all().delete()
        instance.tfa_tokens.all().delete()
        instance.entries.all().delete()
        instance.save()