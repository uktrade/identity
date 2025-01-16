from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django_hawk.utils import DjangoHawkAuthenticationFailed, authenticate_request
from ninja import NinjaAPI

from core.api.main import router as main_router
from core.api.people_finder import router as people_finder_router
from core.api.scim import router as scim_router
from core.api.sso_profile import router as sso_profile_router


def do_hawk_auth(request):
    try:
        authenticate_request(request)
    except DjangoHawkAuthenticationFailed:
        return False


main_api = NinjaAPI(
    title="ID profile API",
    version="1.0.0",
    description="General API for ID retrieval",
    urls_namespace="api",
)
if settings.INFRA_SERVICE == "MAIN":
    main_api.add_router("", main_router)

scim_api = NinjaAPI(
    title="SCIM User Management API",
    version="1.0.0",
    description="SSO-limited API for management of User status",
    urls_namespace="scim",
)
if settings.INFRA_SERVICE == "SSO_SCIM":
    scim_api.add_router("/v2/Users", scim_router)

sso_profile_api = NinjaAPI(
    title="SSO Fast Profile API",
    version="1.0.0",
    description="Optimised minimal profile retrieval API for SSO 'hot-path'",
    urls_namespace="sso-profile",
)
if settings.INFRA_SERVICE == "SSO_PROFILE":
    sso_profile_api.add_router("", sso_profile_router)

people_finder_api = NinjaAPI(
    title="PeopleFinder API",
    version="1.0.0",
    description="PeopleFinder specific API",
    urls_namespace="people-finder",
)
if settings.INFRA_SERVICE == "PEOPLEFINDER":
    people_finder_api.add_router("", people_finder_router)

if settings.APP_ENV not in ("local", "test"):
    main_api.auth = [do_hawk_auth]
    main_api.docs_decorator = staff_member_required
    scim_api.auth = [do_hawk_auth]
    scim_api.docs_decorator = staff_member_required
    sso_profile_api.auth = [do_hawk_auth]
    sso_profile_api.docs_decorator = staff_member_required
    people_finder_api.auth = [do_hawk_auth]
    people_finder_api.docs_decorator = staff_member_required
