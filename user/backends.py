from authbroker_client.backends import AuthbrokerBackend


class IdentityAuthbrokerBackend(AuthbrokerBackend):

    # Overides the default AuthbrokerBackend mapping, as Idenitity only uses email_user_id (sso_email_id) for Users and stores
    # User data in StaffSSOProfile
    def user_create_mapping(self, profile):
        return {}
