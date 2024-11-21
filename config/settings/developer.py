from .base import *


DEBUG = True
ALLOWED_HOSTS = ["localhost"]
INSTALLED_APPS.append(
    "django_extensions",
)

MIDDLEWARE.remove("authbroker_client.middleware.ProtectAllViewsMiddleware")
