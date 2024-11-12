from django.contrib.postgres.fields import ArrayField
from django.db import models
from simple_history.models import HistoricalRecords


class FieldAuthoritativenessMixin:
    is_authoritative: bool = False

    def __init__(self, *args, **kwargs):
        self.is_authoritative = bool(kwargs.pop("is_authoritative", False))
        super().__init__(
            *args,
            **kwargs,
        )


class AuthoritativeCharField(FieldAuthoritativenessMixin, models.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
        ),


class AuthoritativeEmailField(FieldAuthoritativenessMixin, models.EmailField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
        ),


class AuthoritativeUUIDField(FieldAuthoritativenessMixin, models.UUIDField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
        ),


class AuthoritativeArrayField(FieldAuthoritativenessMixin, ArrayField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
        ),


class AbstractHistoricalModel(models.Model):
    class Meta:
        abstract = True

    history = HistoricalRecords(
        inherit=True,
    )
