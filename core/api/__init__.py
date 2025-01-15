from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django_hawk.utils import DjangoHawkAuthenticationFailed, authenticate_request
from ninja import NinjaAPI

from core.api.scim import router as scim_router
from core.api.sso_profile import router as sso_profile_router


def do_hawk_auth(request):
    try:
        authenticate_request(request)
    except DjangoHawkAuthenticationFailed:
        if settings.APP_ENV == "local":
            return True
        return False


protected_apis = NinjaAPI(
    auth=do_hawk_auth,
    docs_decorator=staff_member_required,
)


if settings.INFRA_SERVICE == "SSO_SCIM":
    protected_apis.add_router("/scim/v2/Users", scim_router)
if settings.INFRA_SERVICE == "SSO_PROFILE":
    protected_apis.add_router("/sso", sso_profile_router)
