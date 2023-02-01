from django.db.models import CharField, DateTimeField, EmailField

from knox.settings import CONSTANTS

from reset_password.managers import (
    ResetPasswordLongTokenManager, ResetPasswordShortTokenManager,)
from utils.models import CustomBaseMixin


class ResetPasswordEmailToken(CustomBaseMixin):
    email   = EmailField(blank=False, null=False, editable=False)
    digest  = CharField(max_length=CONSTANTS.DIGEST_LENGTH, primary_key=True)
    expiry  = DateTimeField(null=True, blank=True)

    objects = ResetPasswordLongTokenManager()

    def __str__(self):
        return '%s : %s' % (self.digest, self.email)


class ResetPasswordPhoneToken(CustomBaseMixin):
    email   = EmailField(blank=False, null=False, editable=False)
    digest  = CharField(max_length=CONSTANTS.DIGEST_LENGTH, primary_key=True)
    expiry  = DateTimeField(null=True, blank=True)

    objects = ResetPasswordShortTokenManager()

    def __str__(self):
        return '%s : %s' % (self.digest, self.email)


class ResetPasswordSubmitToken(CustomBaseMixin):
    email   = EmailField(blank=False, null=False, editable=False)
    digest  = CharField(max_length=CONSTANTS.DIGEST_LENGTH, primary_key=True)
    expiry  = DateTimeField(null=True, blank=True)

    objects = ResetPasswordLongTokenManager()

    def __str__(self):
        return '%s : %s' % (self.digest, self.email)