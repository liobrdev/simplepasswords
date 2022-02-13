from re import match
from secrets import choice
from string import ascii_letters, digits

from django.db import IntegrityError
from django.db.models import Model, DateTimeField


def generate_slug() -> str:
    chars = ascii_letters + digits + '-_'
    return ''.join(choice(chars) for i in range(10))


class CustomBaseMixin(Model):
    created_at = DateTimeField(auto_now_add=True, editable=False)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except IntegrityError as e:
            if hasattr(e, 'args') and match((
                r'duplicate key value violates '
                r'unique constraint "[\w-]*_pkey"'
            ), e.args[0]):
                self._set_pk_val(generate_slug())
                self.save(*args, **kwargs)
            else:
                raise e


class DummyUser():
    def __init__(self, email, name):
        self.email = email
        self.name = name