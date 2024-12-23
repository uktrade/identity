from profiles.models import Profile


class ProfileService:
    def get_or_create_profile(
        self,
        profile_type,
        sso_email_id: str,
        first_name: str,
        last_name: str,
        preferred_email: str,
        email_addresses: list[str],
        *args,
        **kwargs,
    ) -> tuple[Profile, bool]:

        profile, created = Profile.objects.get_or_create(
            sso_email_id=sso_email_id,
            first_name=first_name,
            last_name=last_name,
            preferred_email=preferred_email,
            emails=email_addresses,
            *args,
            **kwargs,
        )
        return profile, created

    def get_profile_by_sso_email_id(self, sso_email_id: str) -> Profile:
        """
        Retrieve a user by their ID, only if the user is not soft-deleted.
        """
        return Profile.objects.get(sso_email_id=sso_email_id)
