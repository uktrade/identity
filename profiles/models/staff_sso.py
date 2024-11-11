import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone


class StaffSSOProfile(models.model):
    email = models.EmailField(
        unique=True,
        help_text="Warning: editing this field may cause user profiles to break in Digital Workspace",
    )
    email_user_id = models.EmailField(
        unique=True,
        help_text="A unique user id in an email format",
    )
    user_id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
    )
    first_name = models.CharField(
        max_length=50,
        blank=True,
    )
    last_name = models.CharField(
        max_length=50,
        blank=True,
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
    )
    last_login = models.DateTimeField(
        null=True,
    )
    last_accessed = models.DateTimeField(
        blank=True,
        null=True,
    )
    permitted_applications = ArrayField(
        models.CharField(
            blank=True,
        ),
    )
    application_permission = ArrayField(
        models.CharField(
            blank=True,
        ),
    )
    access_profiles = ArrayField(
        models.CharField(
            blank=True,
        ),
    )
    # permitted_applications = models.ManyToManyField(
    #     settings.OAUTH2_PROVIDER_APPLICATION_MODEL,
    #     related_name="users",
    #     help_text="Applications that this user is permitted to access",
    #     blank=True,
    # )
    # application_permissions = models.ManyToManyField(
    #     ApplicationPermission,
    #     related_name="application_permissions",
    #     help_text=_("Permissions that a user has on in an application"),
    #     blank=True,
    # )

    # access_profiles = models.ManyToManyField(
    #     AccessProfile,
    #     related_name="users",
    #     blank=True,
    # )
