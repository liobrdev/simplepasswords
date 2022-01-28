
from django.contrib.auth.models import AbstractUser
from django.db import IntegrityError
from django.db.models import (
    BooleanField, CharField, EmailField, SlugField, UniqueConstraint, Q,)
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from users.exceptions import DuplicateEmail, DuplicateSuperUser
from users.managers import CustomUserManager
from utils.models import CustomBaseMixin, generate_slug


class CustomUser(AbstractUser, CustomBaseMixin):
    email = EmailField(_('email address'), blank=False)
    name = CharField(_('name'), max_length=255, blank=False)
    phone_number = PhoneNumberField(null=True, blank=True)
    email_is_verified = BooleanField(default=False)
    phone_number_is_verified = BooleanField(default=False)
    tfa_is_enabled = BooleanField(default=False)
    user_slug = SlugField(
        _('user slug'), primary_key=True, unique=True, editable=False,)
    username = None
    first_name = None
    last_name = None

    objects = CustomUserManager()

    USERNAME_FIELD = 'user_slug'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f'user.{self.user_slug}:{self.email}'

    class Meta:
        constraints = [
            # Multiple active accounts may not use the same email address
            UniqueConstraint(
                fields=['email'],
                condition=Q(is_active=True),
                name='unique_active_email',
            ),
            # There can be only one active superuser
            UniqueConstraint(
                fields=['is_superuser', 'is_active'],
                condition=Q(is_superuser=True, is_active=True),
                name='unique_active_superuser',
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.user_slug:
            self.user_slug = generate_slug()

        if not self.email:
            self.email_is_verified = False

        if not self.phone_number:
            self.phone_number_is_verified = False

        if not self.phone_number or not self.phone_number_is_verified:
            self.tfa_is_enabled = False

        try:
            super().save(*args, **kwargs)
        except IntegrityError as e:
            if hasattr(e, 'args') and (
                'duplicate key value violates unique '
                'constraint "unique_active_email"'
            ) in e.args[0]:
                raise DuplicateEmail(self.email)
            if hasattr(e, 'args') and (
                'duplicate key value violates unique '
                'constraint "unique_active_superuser"'
            ) in e.args[0]:
                print(e.args)
                raise DuplicateSuperUser(self.user_slug, self.name, self.email)
            raise e