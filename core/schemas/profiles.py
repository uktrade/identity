from ninja import Field, ModelSchema

from profiles.models.combined import Profile


class ProfileMinimal(ModelSchema):
    id: str = Field(alias="sso_email_id")

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "primary_email",
            "contact_email",
        ]
