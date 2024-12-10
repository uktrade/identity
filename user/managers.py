from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def _create_user(self, sso_email_id, password, **extra_fields):
        if not sso_email_id:
            raise ValueError("The sso_email_id must be set")
        user = self.model(sso_email_id=sso_email_id, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, sso_email_id, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(sso_email_id, password, **extra_fields)

    def create_superuser(self, sso_email_id, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(sso_email_id, password, **extra_fields)
