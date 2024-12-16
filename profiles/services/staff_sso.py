from profiles.models import Email, Profile, StaffSSOProfile, StaffSSOProfileEmail


class StaffSSOService:

    def get_or_create_staff_sso_profile(
        self, emails: list[dict], *args, **kwargs
    ) -> tuple[StaffSSOProfile, bool]:
        """
        Create a new staff sso profile for the specified request.
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
        "user": user_id,
        "first_name": "first name",
        "last_name": "last name",
        """
        staff_sso_profile, profile_created = StaffSSOProfile.objects.get_or_create(
            *args, **kwargs
        )

        # create staff sso email
        for email in emails:
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

    def get_staff_sso_profile_by_id(self, id: str) -> Profile:
        """
        Retrieve a user by their ID, only if the user is not soft-deleted.
        """
        return StaffSSOProfile.objects.get(id=id)
