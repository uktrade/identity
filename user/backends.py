from django.contrib.auth import get_user_model

from authbroker_client.backends import AuthbrokerBackend  # type: ignore
from authbroker_client.utils import get_client, get_profile, has_valid_token

User = get_user_model()


class IdentityAuthbrokerBackend(AuthbrokerBackend):

    def authenticate(self, request, **kwargs):
        client = get_client(request)
        if has_valid_token(client):
            profile = get_profile(client)
            return self.get_or_create_user(profile)
        return None

    # Overides the default AuthbrokerBackend mapping, as Idenitity only uses email_user_id (sso_email_id) for Users and stores
    # User data in StaffSSOProfile
    def user_create_mapping(self, profile):
        return {}
