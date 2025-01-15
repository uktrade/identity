from .base import *


DEBUG = True
ALLOWED_HOSTS = ["localhost", "0.0.0.0"]
INSTALLED_APPS.append(
    "django_extensions",
)

MIDDLEWARE.remove("authbroker_client.middleware.ProtectAllViewsMiddleware")

LOGGING['loggers']["django"]["handlers"] = ["simple"]
LOGGING['loggers']["django.request"]["handlers"] = ["simple"]
LOGGING['loggers']["django.server"]["handlers"] = ["simple"]
LOGGING['loggers']["django.db.backends"]["handlers"] = ["simple"]
