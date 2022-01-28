import os

from django.db.models import Manager
from django.utils import timezone

from knox import crypto


class ResetPasswordLongTokenManager(Manager):
    def create(self, email, expiry):
        token  = crypto.create_token_string()
        salt   = crypto.create_salt_string()
        digest = crypto.hash_token(token, salt)
        expiry = timezone.now() + expiry

        instance = super(ResetPasswordLongTokenManager, self).create(
            email=email,
            salt=salt,
            digest=digest,
            expiry=expiry,
        )

        return instance, token


class ResetPasswordShortTokenManager(Manager):
    def create(self, email, expiry):
        token  = str(int.from_bytes(os.urandom(32), byteorder='big'))[:6]
        salt   = crypto.create_salt_string()
        digest = crypto.hash_token(token, salt)
        expiry = timezone.now() + expiry

        instance = super(ResetPasswordShortTokenManager, self).create(
            email=email,
            salt=salt,
            digest=digest,
            expiry=expiry,
        )

        return instance, token