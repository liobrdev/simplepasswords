from django.contrib.auth.password_validation import validate_password

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer, CharField, RegexField

from reset_password.utils import RPWCommands, check_reset_password_token
from utils import email_regex, error_messages_email


class ResetPasswordRequestSerializer(Serializer):
    email = RegexField(
        email_regex(), error_messages=error_messages_email, write_only=True,)

    def validate_email(self, email):
        return email.lower().strip()


class ResetPasswordEmailSerializer(Serializer):
    email = RegexField(
        email_regex(), error_messages=error_messages_email, write_only=True,)
    email_token = CharField(write_only=True)

    def validate(self, data):
        email       = data.get('email').lower().strip()
        email_token = data.get('email_token')

        try:
            token = check_reset_password_token(
                RPWCommands.RPW_EMAIL, email, email_token,)
        except:
            raise ValidationError('Invalid token.')
        return token.email


class ResetPasswordPhoneSerializer(Serializer):
    email = RegexField(
        email_regex(), error_messages=error_messages_email, write_only=True,)
    email_token = CharField(write_only=True)
    phone_token = CharField(write_only=True)

    def validate(self, data):
        email       = data.get('email').lower().strip()
        email_token = data.get('email_token')
        phone_token = data.get('phone_token')

        try:
            check_reset_password_token(
                RPWCommands.RPW_EMAIL, email, email_token,)
            token = check_reset_password_token(
                RPWCommands.RPW_PHONE, email, phone_token,)
        except:
            raise ValidationError('Invalid token.')
        return token.email


class ResetPasswordSubmitSerializer(Serializer):
    email = RegexField(
        email_regex(), error_messages=error_messages_email, write_only=True,)
    password        = CharField(trim_whitespace=False, write_only=True)
    password_2      = CharField(trim_whitespace=False, write_only=True)
    email_token     = CharField(write_only=True)
    phone_token     = CharField(write_only=True)
    submit_token    = CharField(write_only=True)
    
    def validate(self, data):
        email           = data.get('email').lower().strip()
        password        = data.get('password')
        password_2      = data.get('password_2')
        email_token     = data.get('email_token')
        phone_token     = data.get('phone_token')
        submit_token    = data.get('submit_token')

        try:
            check_reset_password_token(
                RPWCommands.RPW_EMAIL, email, email_token,)
            check_reset_password_token(
                RPWCommands.RPW_PHONE, email, phone_token,)
            check_reset_password_token(
                RPWCommands.RPW_SUBMIT, email, submit_token,)
        except:
            raise ValidationError('Invalid token.')

        if password != password_2:
            raise ValidationError('Passwords do not match.')

        if not validate_password(password):
            return dict(email=email, password=password)
        raise ValidationError('Cannot reset password with the provided info.')