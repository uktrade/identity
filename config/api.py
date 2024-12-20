from django.contrib.admin.views.decorators import staff_member_required
from django_hawk.utils import authenticate_request, DjangoHawkAuthenticationFailed
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
