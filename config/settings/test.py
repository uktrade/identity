import logging

from .base import *  # noqa


APP_ENV = "test"
DEBUG = True
TEMPLATE_DEBUG = True

STORAGES["staticfiles"][
    "BACKEND"
] = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Required for tests to bypass SSO.
MIDDLEWARE.remove("authbroker_client.middleware.ProtectAllViewsMiddleware")  # noqa

# Turn off Celery
CELERY_ALWAYS_EAGER = True

logging.disable(logging.WARN)
