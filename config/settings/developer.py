from .base import *


HOST_ALL_APIS = True

DEBUG = True
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "*"]
INSTALLED_APPS.append(
    "django_extensions",
)

if "authbroker_client.middleware.ProtectAllViewsMiddleware" in MIDDLEWARE:
    MIDDLEWARE.remove("authbroker_client.middleware.ProtectAllViewsMiddleware")

LOGGING["loggers"]["django"]["handlers"] = ["simple"]  #  type:ignore
LOGGING["loggers"]["django.request"]["handlers"] = ["simple"]  #  type:ignore
LOGGING["loggers"]["django.server"]["handlers"] = ["simple"]  #  type:ignore
LOGGING["loggers"]["django.db.backends"]["handlers"] = ["simple"]  #  type:ignore
LOGGING["loggers"]["mohawk"]["handlers"] = ["simple"]  #  type:ignore
