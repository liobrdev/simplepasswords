import logging

from cryptocode import decrypt, encrypt
from django.contrib.auth import get_user_model, password_validation
from django.db.models import F

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    Serializer, ModelSerializer, Field, CharField, RegexField,)

from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.serializerfields import PhoneNumberField

from users.exceptions import DuplicateEmail
from users.utils import UserCommands
from utils import (
    email_regex, name_regex, parse_request_metadata,
    error_messages_email, error_messages_name,)


logger = logging.getLogger(__name__)


class TruncatedPhoneNumberField(Field):
    def get_attribute(self, instance):
        phone_number = instance.phone_number
        if not phone_number or not isinstance(phone_number, PhoneNumber):
            return ''
        return phone_number

    def to_representation(self, value):
        if not value or not isinstance(value, PhoneNumber):
            return ''
        phone_number_string = value.as_e164
        asterisks_substring = (len(phone_number_string) - 4) * '*'
        return asterisks_substring + phone_number_string[-4:]


class ReadOnlyUserSerializer(ModelSerializer):
    truncated_phone_number = TruncatedPhoneNumberField()

    class Meta:
        model = get_user_model()
        fields = (
            'user_slug', 'name', 'email', 'email_is_verified',
            'phone_number_is_verified', 'truncated_phone_number',
            'tfa_is_enabled',)
        read_only_fields = (
            'user_slug', 'name', 'email', 'email_is_verified',
            'phone_number_is_verified', 'truncated_phone_number',
            'tfa_is_enabled',)


class UserSerializer(ModelSerializer):
    name = RegexField(
        name_regex(), error_messages=error_messages_name, required=False,)
    email = RegexField(
        email_regex(),
        error_messages=error_messages_email, required=False,)
    truncated_phone_number = TruncatedPhoneNumberField(read_only=True)
    phone_number = PhoneNumberField(
        write_only=True, required=False, allow_blank=True, allow_null=True,)
    password = CharField(
        write_only=True, required=False, allow_blank=True,)
    password_2 = CharField(
        write_only=True, required=False, allow_blank=True,)
    current_password = CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = (
            'user_slug', 'name', 'email', 'email_is_verified',
            'phone_number_is_verified', 'truncated_phone_number',
            'phone_number', 'tfa_is_enabled', 'password', 'password_2',
            'current_password',)
        read_only_fields = (
            'user_slug', 'email_is_verified', 'phone_number_is_verified',
            'truncated_phone_number',)
    
    def validate_phone_number(self, phone_number):
        if not phone_number:
            return ''
        else:
            return phone_number
    
    def validate_tfa_is_enabled(self, tfa_is_enabled):
        request = self.context['request']
        user = request.user

        if tfa_is_enabled and (
            not user.phone_number or
            not user.phone_number_is_verified
        ):
            msg = (
                'A verified phone number is required ' +
                'in order to enable two-factor authentication.')
            raise ValidationError(msg)
        return tfa_is_enabled

    def validate_password(self, password):
        request = self.context['request']
        user = request.user

        if password and not password_validation.validate_password(
            password, user,
        ):
            if password == user.user_slug:
                raise ValidationError('Password cannot be your user ID.')
            return password
        elif not password:
            return None

    def validate_password_2(self, password_2):
        return self.validate_password(password_2)

    def validate_current_password(self, current_password):
        request = self.context['request']
        user = request.user

        if user.check_password(current_password):
            return current_password
        raise ValidationError('Invalid password.')

    def save(self):
        current_password = self.validated_data.pop('current_password')

        request = self.context['request']
        user = request.user

        user.name = self.validated_data.get('name', user.name)
        user.tfa_is_enabled = self.validated_data.get(
            'tfa_is_enabled', user.tfa_is_enabled,)

        email           = self.validated_data.get('email', None)
        phone_number    = self.validated_data.get('phone_number', None)
        password        = self.validated_data.get('password', None)
        password_2      = self.validated_data.get('password_2', None)

        if email is not None and email != user.email:
            user.email = email
            user.email_is_verified = False

        if phone_number is not None and phone_number != user.phone_number:
            user.phone_number = phone_number
            user.phone_number_is_verified = False

        if password:
            if not password_2 or password_2 != password:
                e = ValidationError({
                    'password_2': ['Passwords do not match.'],
                })
                logger.exception('Error changing user password.', exc_info=e, extra={
                    'user': user.user_slug,
                    'command': UserCommands.UPDATE,
                    'client_ip': request.META['CLIENT_IP'],
                    'metadata': parse_request_metadata(request),
                })
                raise e

            user.set_password(password)

            entries = user.entries.all()
            for entry in entries:
                entry.value = encrypt(
                    decrypt(entry.value, current_password), password,)
                entry.save()

        elif password_2:
            e = ValidationError({
                'password': ['Invalid password change.'],
            })
            logger.exception('Error changing user password.', exc_info=e, extra={
                'user': user.user_slug,
                'command': UserCommands.UPDATE,
                'client_ip': request.META['CLIENT_IP'],
                'metadata': parse_request_metadata(request),
            })
            raise e

        try:
            user.save()
        except DuplicateEmail:
            raise ValidationError({
                'email': [
                    'Email address unavailable - please choose a different one.',
                ],
            })
        return user


class UserDeactivateSerializer(Serializer):
    email = RegexField(
        email_regex(), error_messages=error_messages_email, write_only=True,)
    current_password = CharField(trim_whitespace=False, write_only=True)

    def validate_email(self, value):
        email = value.lower()
        request = self.context['request']
        user = request.user
        if email == user.email:
            return email
        raise ValidationError('Invalid email.')

    def validate_current_password(self, current_password):
        request = self.context['request']
        user = request.user
        if user.check_password(current_password):
            return True
        raise ValidationError('Invalid password.')