import logging

from cryptocode import decrypt
from django.http.response import Http404

from rest_framework.exceptions import Throttled, ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    UpdateAPIView,)
from rest_framework.mixins import DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

from entries.serializers import EntrySerializer, ListEntrySerializer
from entries.utils import EntryCommands
from utils import parse_request_metadata
from utils.exceptions import RequestError
from utils.throttling import throttle_command


logger = logging.getLogger(__name__)

class ListCreateEntriesAPI(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['title']
    ordering_fields = ['created_at']
    ordering = '-created_at'

    def get_queryset(self):
        return self.request.user.entries.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EntrySerializer
        return ListEntrySerializer

    def create(self, request, *args, **kwargs):
        try:
            if throttle_command(
                EntryCommands.CREATE_ENTRY,
                request.META['CLIENT_IP'],
                request,
            ):
                raise Throttled()

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer = self.perform_create(serializer)

            response = Response(
                serializer.data, status=HTTP_201_CREATED,
                headers=self.get_success_headers(serializer.data),)
            return response
        except (Throttled, ValidationError) as e:
            raise e
        except Exception as e:
            logger.exception('Error creating entry.', exc_info=e, extra={
                'user': request.user.user_slug,
                'command': EntryCommands.CREATE_ENTRY,
                'client_ip': request.META['CLIENT_IP'],
                'metadata': parse_request_metadata(request),
            })
            raise RequestError('Error creating entry.')

    def perform_create(self, serializer):
        instance = serializer.save()
        return ListEntrySerializer(instance)


class RetrieveEntryAPI(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EntrySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return self.request.user.entries.all()

    def post(self, request, *args, **kwargs):
        try:
            if throttle_command(
                EntryCommands.RETRIEVE_ENTRY,
                request.META['CLIENT_IP'],
                request,
            ):
                raise Throttled()

            user = request.user
            password = request.data.pop('password')

            if not user.check_password(password):
                raise ValidationError({ 'password': ['Invalid password.'] })

            instance = self.get_object()
            instance.value = decrypt(instance.value, password)

            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except (Http404, Throttled, ValidationError) as e:
            raise e
        except Exception as e:
            logger.exception('Error retrieving entry.', exc_info=e, extra={
                'user': request.user.user_slug,
                'command': EntryCommands.RETRIEVE_ENTRY,
                'client_ip': request.META['CLIENT_IP'],
                'metadata': parse_request_metadata(request),
            })
            raise RequestError('Error retrieving entry.')


class UpdateEntryAPI(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EntrySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return self.request.user.entries.all()

    def update(self, request, *args, **kwargs):
        try:
            if throttle_command(
                EntryCommands.UPDATE_ENTRY,
                request.META['CLIENT_IP'],
                request,
            ):
                raise Throttled()
            return super().update(request, *args, **kwargs)
        except (Http404, Throttled, ValidationError) as e:
            raise e
        except Exception as e:
            logger.exception('Error updating entry.', exc_info=e, extra={
                'user': request.user.user_slug,
                'command': EntryCommands.UPDATE_ENTRY,
                'client_ip': request.META['CLIENT_IP'],
                'metadata': parse_request_metadata(request),
            })
            raise RequestError('Error updating entry.')


class DestroyEntryAPI(DestroyModelMixin, GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EntrySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return self.request.user.entries.all()

    def post(self, request, *args, **kwargs):
        try:
            if throttle_command(
                EntryCommands.DESTROY_ENTRY,
                request.META['CLIENT_IP'],
                request,
            ):
                raise Throttled()

            user = request.user
            password = request.data.pop('password')

            if not user.check_password(password):
                raise ValidationError('Invalid password.')

            return super().destroy(request, *args, **kwargs)
        except (Http404, Throttled, ValidationError) as e:
            raise e
        except Exception as e:
            logger.exception('Error destroying entry.', exc_info=e, extra={
                'user': request.user.user_slug,
                'command': EntryCommands.DESTROY_ENTRY,
                'client_ip': request.META['CLIENT_IP'],
                'metadata': parse_request_metadata(request),
            })
            raise RequestError('Error destroying entry.')