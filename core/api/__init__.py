from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django_hawk.utils import DjangoHawkAuthenticationFailed, authenticate_request
from ninja import NinjaAPI


def do_hawk_auth(request):
    try:
        authenticate_request(request)
    except DjangoHawkAuthenticationFailed:
        return False

protected_apis = NinjaAPI(
    auth=do_hawk_auth,
    docs_decorator=staff_member_required,
)

if settings.APP_ENV == "local":
    protected_apis = NinjaAPI()
