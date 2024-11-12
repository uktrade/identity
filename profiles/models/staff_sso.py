import uuid

from django.db import models

from profiles.models.base_models import (
    AbstractHistoricalModel,
    AuthoritativeArrayField,
    AuthoritativeCharField,
    AuthoritativeEmailField,
    AuthoritativeUUIDField,
)


class StaffSSOProfile(AbstractHistoricalModel):
    email = AuthoritativeEmailField(
        unique=True,
        is_authoritative=True,
    )
    contact_email = AuthoritativeEmailField(
        unique=True,
    )
    email_user_id = AuthoritativeEmailField(
        unique=True,
        help_text="A unique user id in an email format",
    )
    user_id = AuthoritativeUUIDField(
        unique=True,
        default=uuid.uuid4,
    )
    first_name = AuthoritativeCharField(
        max_length=50,
        blank=True,
    )
    last_name = AuthoritativeCharField(
        max_length=50,
        blank=True,
    )
    other_emails = AuthoritativeArrayField(
        models.EmailField(
            unique=True,
        ),
        blank=True,
    )
