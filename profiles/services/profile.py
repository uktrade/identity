from django.contrib.auth.base_user import BaseUserManager

from profiles.models import Profile, StaffSSOProfile


class ProfileService:
    def get_or_create_profile(
        self, staff_sso_profile: StaffSSOProfile
    ) -> tuple[Profile, bool]:
        # create combined profile

        emails = staff_sso_profile.emails.all()
        preferred_email = emails[0].email.__str__()
        email_addresses = list()
        for email in emails:
            email_addresses.append(
                BaseUserManager.normalize_email(email.email.__str__())
            )
            if email.preferred:
                preferred_email = email.email.__str__()

        profile, created = Profile.objects.get_or_create(
            sso_email_id=staff_sso_profile.user.sso_email_id,
            first_name=staff_sso_profile.first_name,
            last_name=staff_sso_profile.last_name,
            preferred_email=preferred_email,
            emails=email_addresses,
        )
        return profile, created

    def get_profile_by_sso_email_id(self, sso_email_id: str) -> Profile:
        """
        Retrieve a user by their ID, only if the user is not soft-deleted.
        """
        return Profile.objects.get(sso_email_id=sso_email_id)
