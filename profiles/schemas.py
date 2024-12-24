from ninja import Field, ModelSchema

from profiles.models.generic import Profile


class ProfileMinimal(ModelSchema):
    id: str = Field(alias="sso_email_id")

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "preferred_email",
        ]
