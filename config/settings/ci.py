import logging

from .base import *  # noqa


APP_ENV = "ci"
DEBUG = True
TEMPLATE_DEBUG = True

# Required for tests to bypass SSO.
MIDDLEWARE.remove("authbroker_client.middleware.ProtectAllViewsMiddleware")  # noqa

# Turn off Celery
CELERY_ALWAYS_EAGER = True

logging.disable(logging.WARN)