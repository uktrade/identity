from .base import *


DEBUG = True
ALLOWED_HOSTS = ["localhost", "0.0.0.0"]
INSTALLED_APPS.append(
    "django_extensions",
)

MIDDLEWARE.remove("authbroker_client.middleware.ProtectAllViewsMiddleware")
