from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django_hawk.utils import DjangoHawkAuthenticationFailed, authenticate_request
from ninja import NinjaAPI

from core.api.main import router as main_router
from core.api.people_finder import router as people_finder_router
from core.api.scim import router as scim_router
from core.api.sso_profile import router as sso_profile_router


def do_hawk_auth(request) -> bool:
    if settings.APP_ENV in ("local", "test"):
        return True
    try:
        return authenticate_request(request)
    except DjangoHawkAuthenticationFailed:
        return False


main_api = NinjaAPI(
    title="ID profile API",
    version="1.0.0",
    description="General API for ID retrieval",
    urls_namespace="api",
    auth=[do_hawk_auth],
    docs_decorator=staff_member_required,
)
if settings.INFRA_SERVICE == "MAIN" or settings.HOST_ALL_APIS:
    main_api.add_router("", main_router)

scim_api = NinjaAPI(
    title="SCIM User Management API",
    version="1.0.0",
    description="SSO-limited API for management of User status",
    urls_namespace="scim",
    auth=[do_hawk_auth],
    docs_decorator=staff_member_required,
)
if settings.INFRA_SERVICE == "SSO_SCIM" or settings.HOST_ALL_APIS:
    scim_api.add_router("/v2/Users", scim_router)

sso_profile_api = NinjaAPI(
    title="SSO Fast Profile API",
    version="1.0.0",
    description="Optimised minimal profile retrieval API for SSO 'hot-path'",
    urls_namespace="sso-profile",
    auth=[do_hawk_auth],
    docs_decorator=staff_member_required,
)
if settings.INFRA_SERVICE == "SSO_PROFILE" or settings.HOST_ALL_APIS:
    sso_profile_api.add_router("", sso_profile_router)

people_finder_api = NinjaAPI(
    title="PeopleFinder API",
    version="1.0.0",
    description="PeopleFinder specific API",
    urls_namespace="people-finder",
    auth=[do_hawk_auth],
    docs_decorator=staff_member_required,
)
if settings.INFRA_SERVICE == "PEOPLEFINDER" or settings.HOST_ALL_APIS:
    people_finder_api.add_router("", people_finder_router)

if settings.APP_ENV == "local":
    main_api.docs_decorator = None
    scim_api.docs_decorator = None
    sso_profile_api.docs_decorator = None
    people_finder_api.docs_decorator = None
