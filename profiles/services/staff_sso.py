from core.utils import update_model_fields
from profiles.models import Email, Profile, StaffSSOProfile, StaffSSOProfileEmail
from user.models import User


class StaffSSOService:

    def get_or_create_staff_sso_profile(
        self,
        user: User,
        first_name: str,
        last_name: str,
        emails: list[dict],
        *args,
        **kwargs,
    ) -> tuple[StaffSSOProfile, bool]:
        """
        Create a new staff sso profile for the specified request.
        """
        staff_sso_profile, profile_created = StaffSSOProfile.objects.get_or_create(
            user=user, first_name=first_name, last_name=last_name, *args, **kwargs
        )

        # create staff sso email records
        for email in emails:
            email_object, email_created = Email.objects.get_or_create(
                address=email["address"],
            )
            self.get_or_create_staff_sso_email(
                profile=staff_sso_profile,
                email=email_object,
                type=email["type"],
                preferred=email["preferred"],
            )

        return staff_sso_profile, profile_created

    def get_or_create_staff_sso_email(
        self,
        profile: StaffSSOProfile,
        email: StaffSSOProfileEmail,
        type: str,
        preferred: bool,
        *args,
        **kwargs,
    ) -> tuple[StaffSSOProfileEmail, bool]:
        """
        Create a new staff sso email
        """
        staff_sso_email, created = StaffSSOProfileEmail.objects.get_or_create(
            profile=profile,
            email=email,
            type=type,
            preferred=preferred,
            *args,
            **kwargs,
        )
        return staff_sso_email, created

    def update_staff_sso_email(
        self,
        *args,
        **kwargs,
    ) -> StaffSSOProfileEmail:
        """
        Create a new staff sso email
        """

        valid_fields = [
            "profile",
            "email",
            "type",
            "preferred",
        ]
        staff_sso_profile_email = StaffSSOProfileEmail.objects.filter(
            email=kwargs["email"]
        )[0]
        return update_model_fields(kwargs, staff_sso_profile_email, valid_fields)

    def get_staff_sso_profile_by_id(self, id: int) -> Profile:
        """
        Retrieve a user by their ID, only if the user is not soft-deleted.
        """
        return StaffSSOProfile.objects.get(id=id)

    def update_staff_sso_profile(
        self,
        id: int,
        *args,
        **kwargs,
    ) -> Profile:

        staff_sso_profile = self.get_staff_sso_profile_by_id(id)

        if "emails" in kwargs:
            # create staff sso email records
            for email in kwargs["emails"]:
                email_object, _ = Email.objects.get_or_create(
                    address=email["address"],
                )
                self.update_staff_sso_email(
                    profile=staff_sso_profile,
                    email=email_object,
                    type=email["type"],
                    preferred=email["preferred"],
                )

        if "first_name" in kwargs:
            staff_sso_profile.first_name = kwargs["first_name"]
        if "last_name" in kwargs:
            staff_sso_profile.last_name = kwargs["last_name"]

        staff_sso_profile.save()
        return staff_sso_profile
