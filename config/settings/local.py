from .base import *


DEBUG: bool = True
ALLOWED_HOSTS: list[str] = ["localhost"]
INSTALLED_APPS.append(
    "django_extensions",
)
