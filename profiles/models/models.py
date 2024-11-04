from django.contrib.auth import get_user_model
from django.db import models as django_models
from simple_history.models import HistoricalRecords


class FieldAuthoritativenessMixin:
    is_authoritative: bool = False

    def __init__(self, *args, **kwargs):
        self.is_authoritative = bool(kwargs.pop("is_authoritative", False))
        super().__init__(
            *args,
            **kwargs,
        )


class AuthoritativeCharField(FieldAuthoritativenessMixin, django_models.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
        ),


class AbstractHistoricalModel(django_models.Model):
    class Meta:
        abstract = True

    history = HistoricalRecords(
        inherit=True,
    )


class AbstractProfile(AbstractHistoricalModel):
    class Meta:
        abstract = True

    user = django_models.OneToOneField(
        get_user_model(),
        on_delete=django_models.CASCADE,
    )

    def __str__(self):
        return self.user.username
