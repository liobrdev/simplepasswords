from django.conf import settings
from django.db.models import CharField, DateTimeField, ForeignKey, PROTECT

from knox.settings import CONSTANTS

from authentication.managers import (
    EmailVerificationTokenManager, PhoneVerificationTokenManager,
    TwoFactorAuthTokenManager,)
from utils.models import CustomBaseMixin


class EmailVerificationToken(CustomBaseMixin):
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=PROTECT,
        related_name='email_verification_tokens',
        editable=False,)
    token_key = CharField(max_length=CONSTANTS.TOKEN_KEY_LENGTH, db_index=True)
    salt      = CharField(max_length=CONSTANTS.SALT_LENGTH, unique=True)
    digest    = CharField(max_length=CONSTANTS.DIGEST_LENGTH, primary_key=True)
    expiry    = DateTimeField(null=True, blank=True)

    objects = EmailVerificationTokenManager()

    def __str__(self):
        return '%s : %s' % (self.digest, self.user.email)


class PhoneVerificationToken(CustomBaseMixin):
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=PROTECT,
        related_name='phone_verification_tokens',
        editable=False,)
    salt   = CharField(max_length=CONSTANTS.SALT_LENGTH, unique=True)
    digest = CharField(max_length=CONSTANTS.DIGEST_LENGTH, primary_key=True)
    expiry = DateTimeField(null=True, blank=True)

    objects = PhoneVerificationTokenManager()

    def __str__(self):
        return '%s : %s' % (self.digest, self.user.email)


class TwoFactorAuthToken(CustomBaseMixin):
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=PROTECT,
        related_name='tfa_tokens',
        editable=False,)
    salt   = CharField(max_length=CONSTANTS.SALT_LENGTH, unique=True)
    digest = CharField(max_length=CONSTANTS.DIGEST_LENGTH, primary_key=True)
    expiry = DateTimeField(null=True, blank=True)

    objects = TwoFactorAuthTokenManager()

    def __str__(self):
        return '%s : %s' % (self.digest, self.user.email)