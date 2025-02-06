from django.db import models


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
