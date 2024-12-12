from django.contrib.auth.base_user import BaseUserManager

from profiles.models import (
    CombinedProfile,
    Email,
    StaffSSOProfileEmail,
    StaffSSOProfile,
)


class ProfileService:

    def get_or_create_staff_sso_profile(
        self, profile_request: dict
    ) -> tuple[StaffSSOProfile, bool]:
        """
        Create a new staff sso profile for the specified request.
        profile_request = {
            "user": user_id,
            "first_name": "first name",
            "last_name": "last name",
            "emails": [
                {
                    "address": "email1@email.com",
                    "type": "work",
                    "preferred": False
                },
                {
                    "address": "email2@email.com",
                    "type": "contact",
                    "preferred": True
                }
            ],
        }
        """
        staff_sso_profile, profile_created = StaffSSOProfile.objects.get_or_create(
            user=profile_request["user"],
            first_name=profile_request["first_name"],
            last_name=profile_request["last_name"],
        )

        # create staff sso email
        for email in profile_request["emails"]:
            email_object, email_created = Email.objects.get_or_create(
                address=email["address"],
            )
            staff_sso_email_request = {
                "profile": staff_sso_profile,
                "email": email_object,
                "type": email["type"],
                "preferred": email["preferred"],
            }
            self.get_or_create_staff_sso_email(staff_sso_email_request)

        return staff_sso_profile, profile_created

    def get_or_create_staff_sso_email(
        self, staff_sso_email_request: dict
    ) -> tuple[StaffSSOProfileEmail, bool]:
        """
        Create a new staff sso email
        """
        staff_sso_email, created = StaffSSOProfileEmail.objects.get_or_create(
            profile=staff_sso_email_request["profile"],
            email=staff_sso_email_request["email"],
            type=staff_sso_email_request["type"],
            preferred=staff_sso_email_request["preferred"],
        )
        return staff_sso_email, created

    def get_or_create_combined_profile(
        self, staff_sso_profile: StaffSSOProfile
    ) -> tuple[CombinedProfile, bool]:
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

        combined_profile, created = CombinedProfile.objects.get_or_create(
            sso_email_id=staff_sso_profile.user.sso_email_id,
            first_name=staff_sso_profile.first_name,
            last_name=staff_sso_profile.last_name,
            preferred_email=preferred_email,
            emails=email_addresses,
        )
        return combined_profile, created

    def get_combined_profile_by_sso_email_id(
        self, sso_email_id: str
    ) -> CombinedProfile:
        """
        Retrieve a user by their ID, only if the user is not soft-deleted.
        """
        return CombinedProfile.objects.get(sso_email_id=sso_email_id)

    def get_staff_sso_profile_by_id(self, id: str) -> CombinedProfile:
        """
        Retrieve a user by their ID, only if the user is not soft-deleted.
        """
        return StaffSSOProfile.objects.get(id=id)
