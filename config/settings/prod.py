from .base import *  # noqa


DEBUG = False

AWS_QUERYSTRING_AUTH = False

SESSION_COOKIE_AGE: int = 60 * 60

SECURE_BROWSER_XSS_FILTER: bool = True
X_FRAME_OPTIONS: str = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF: bool = True
SECURE_HSTS_SECONDS: int = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = True
SECURE_HSTS_PRELOAD: bool = True
SECURE_SSL_REDIRECT: bool = True
CSRF_COOKIE_SECURE: bool = True
SESSION_COOKIE_SECURE: bool = True
SECURE_PROXY_SSL_HEADER: tuple[str, str] = ("HTTP_X_FORWARDED_PROTO", "https")
# Don't redirect from HTTP to HTTPS on the health check endpoint or /api/*
SECURE_REDIRECT_EXEMPT = [r"^.*ping\.xml$", r"^api\/.*$"]
