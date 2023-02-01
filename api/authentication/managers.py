import os

from django.db.models import Manager
from django.utils import timezone

from knox import crypto


class EmailVerificationTokenManager(Manager):
    def create(self, user, expiry):
        token  = crypto.create_token_string()
        digest = crypto.hash_token(token)
        expiry = timezone.now() + expiry

        instance = super(EmailVerificationTokenManager, self).create(
            user=user,
            digest=digest,
            expiry=expiry,
        )

        return instance, token


class PhoneVerificationTokenManager(Manager):
    def create(self, user, expiry):
        token  = str(int.from_bytes(os.urandom(32), byteorder='big'))[:6]
        digest = crypto.hash_token(token)
        expiry = timezone.now() + expiry

        instance = super(PhoneVerificationTokenManager, self).create(
            user=user,
            digest=digest,
            expiry=expiry,
        )

        return instance, token


class TwoFactorAuthTokenManager(Manager):
    def create(self, user, expiry):
        token  = crypto.create_token_string()
        digest = crypto.hash_token(token)
        expiry = timezone.now() + expiry

        instance = super(TwoFactorAuthTokenManager, self).create(
            user=user,
            digest=digest,
            expiry=expiry,
        )

        return instance, token