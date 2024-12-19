from core.utils import update_model_fields
from profiles.models import Profile


class ProfileService:
    def get_or_create_profile(
        self,
        sso_email_id: str,
        first_name: str,
        last_name: str,
        preferred_email: str,
        emails: list[str],
        *args,
        **kwargs,
    ) -> tuple[Profile, bool]:

        profile, created = Profile.objects.get_or_create(
            sso_email_id=sso_email_id,
            first_name=first_name,
            last_name=last_name,
            preferred_email=preferred_email,
            emails=emails,
            *args,
            **kwargs,
        )
        return profile, created

    def get_profile_by_sso_email_id(self, sso_email_id: str) -> Profile:
        """
        Retrieve a user by their ID, only if the user is not soft-deleted.
        """
        return Profile.objects.get(sso_email_id=sso_email_id)

    def update_profile(
        self,
        sso_email_id: str,
        *args,
        **kwargs,
    ) -> Profile:
        profile = self.get_profile_by_sso_email_id(sso_email_id)

        # Validate that only valid fields are being updated
        valid_fields = [
            "sso_email_id",
            "first_name",
            "last_name",
            "preferred_email",
            "emails",
        ]
        return update_model_fields(kwargs, profile, valid_fields)

    def delete_profile(self, sso_email_id: str) -> Profile:
        """
        Retrieve a user by their ID, only if the user is not soft-deleted.
        """
        profile = Profile.objects.get(sso_email_id=sso_email_id)
        profile.is_active = False
        profile.save()
        return profile
