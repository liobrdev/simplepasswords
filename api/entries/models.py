from django.conf import settings
from django.db.models import (
    CharField,
    ForeignKey,
    SlugField,
    TextField,
    PROTECT,)

from utils.models import CustomBaseMixin, generate_slug


class Entry(CustomBaseMixin):
    slug = SlugField(
        primary_key=True,
        editable=False,
        default=generate_slug,)
    title = CharField(max_length=255)
    value = TextField()
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=PROTECT,
        related_name='entries',
        editable=False,)

    class Meta:
        ordering = ['-created_at']