try:
    from hmac import compare_digest
except ImportError:
    def compare_digest(a, b):
        return a == b

import binascii
import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.db.models.enums import TextChoices
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from knox.crypto import hash_token
from twilio.rest import Client
from urllib import parse

from reset_password.models import (
    ResetPasswordEmailToken, ResetPasswordPhoneToken,
    ResetPasswordSubmitToken,)
from reset_password.utils import RPWCommands


client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


class RPWCommands(TextChoices):
    RPW_REQUEST = 'reset_password_request'
    RPW_EMAIL = 'reset_password_email'
    RPW_PHONE = 'reset_password_phone'
    RPW_SUBMIT = 'reset_password_submit'


def send_reset_password_email(email, token_string, device_name, browser_name):
    token = parse.quote(token_string)
    device_name = device_name.strip()
    browser_name = browser_name.strip()

    protocol = 'http'
    if not settings.DEBUG:
        protocol += 's'

    device_indefinite_article = 'a'

    if re.match('^[aeiou]{1}.*$', device_name, re.IGNORECASE):
        device_indefinite_article += 'n'

    link = f'{protocol}://{settings.DOMAIN}/reset_password/email?token={token}'

    html_message = render_to_string(
        'email_reset_password.html',
        {
            'device_name_phrase': f'{device_indefinite_article} {device_name}',
            'browser_name': browser_name,
            'link_reset_password': link,
        },
    )

    plain_message = strip_tags(html_message)

    send_mail(
        'Reset password for SimplePasswords account', plain_message,
        'support@simplepasswords.app', [email], html_message=html_message,)


def send_reset_password_sms(to, from_, token_string):
    body = f'Security code for SimplePasswords: {token_string}'
    client.messages.create(to=to, from_=from_, body=body)


def check_reset_password_token(command, email, token_string):
    if command == RPWCommands.RPW_EMAIL:
        Token = ResetPasswordEmailToken
    elif command == RPWCommands.RPW_PHONE:
        Token = ResetPasswordPhoneToken
    elif command == RPWCommands.RPW_SUBMIT:
        Token = ResetPasswordSubmitToken
    else:
        raise ImproperlyConfigured(f"Invalid verification command '{command}'")

    for token in Token.objects.filter(email=email):
        if token.expiry <= timezone.now():
            token.delete()
            continue
        try:
            digest = hash_token(token_string, token.salt)
        except (TypeError, binascii.Error):
            continue
        if compare_digest(digest, token.digest):
            return token
        continue
    raise