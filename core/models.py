from enum import StrEnum

from django.db import models


# ideally these move to a generic S3 Bulk Importer package
class IngestedModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_not_deleted_upstream=True)


class IngestedModel(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_not_deleted_upstream = models.BooleanField(default=True)

    objects = IngestedModelManager()


from django import forms
from django.contrib.postgres.fields import ArrayField


class _TypedMultipleChoiceField(forms.TypedMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.pop("base_field", None)
        kwargs.pop("max_length", None)
        super().__init__(*args, **kwargs)


# from https://gist.github.com/danni/f55c4ce19598b2b345ef
class ChoiceArrayField(ArrayField):
    """
    A field that allows us to store an array of choices.

    Uses Django 4.2's postgres ArrayField
    and a TypeMultipleChoiceField for its formfield.

    Usage:

        choices = ChoiceArrayField(
            models.CharField(max_length=..., choices=(...,)), blank=[...], default=[...]
        )
    """

    def formfield(self, **kwargs):
        defaults = {
            "form_class": _TypedMultipleChoiceField,
            "choices": self.base_field.choices,
            "coerce": self.base_field.to_python,
        }
        defaults.update(kwargs)
        # Skip our parent's formfield implementation completely as we don't care for it.
        # pylint:disable=bad-super-call
        return super().formfield(**defaults)
