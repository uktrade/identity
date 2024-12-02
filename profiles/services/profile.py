from profiles.models import CombinedProfile, Email, StaffSSOEmail, StaffSSOProfile

from django.contrib.auth.base_user import BaseUserManager


class ProfileService:
    def __init__(self):
        self.user_manager = BaseUserManager()

    def create_staff_sso_profile(
        self, profile_request: dict
    ) -> tuple[CombinedProfile, bool]:
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
            self.create_staff_sso_email(staff_sso_email_request)

        # create combined profile
        combined_profile_request = {
            "sso_email_id": staff_sso_profile.user.sso_email_id,
            "first_name": staff_sso_profile.first_name,
            "last_name": staff_sso_profile.last_name,
            "emails": staff_sso_profile.emails.all(),
        }
        combined_profile, combined_profile_created = self.create_combined_profile(
            combined_profile_request
        )

        return combined_profile, combined_profile_created

    def create_staff_sso_email(
        self, staff_sso_email_request: dict
    ) -> tuple[StaffSSOEmail, bool]:
        """
        Create a new staff sso email
        """
        staff_sso_email, created = StaffSSOEmail.objects.get_or_create(
            profile=staff_sso_email_request["profile"],
            email=staff_sso_email_request["email"],
            type=staff_sso_email_request["type"],
            preferred=staff_sso_email_request["preferred"],
        )
        return staff_sso_email, created

    def create_combined_profile(
        self, combined_profile_request: dict
    ) -> tuple[CombinedProfile, bool]:
        # create combined profile
        emails = combined_profile_request["emails"]
        preferred_email = emails[0].email.__str__()
        email_addresses = list()
        for email in emails:
            email_addresses.append(
                self.user_manager.normalize_email(email.email.__str__())
            )
            if email.preferred:
                preferred_email = email.email.__str__()

        combined_profile, created = CombinedProfile.objects.get_or_create(
            sso_email_id=combined_profile_request["sso_email_id"],
            first_name=combined_profile_request["first_name"],
            last_name=combined_profile_request["last_name"],
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
