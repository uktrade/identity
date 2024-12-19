from django.conf import settings
from ninja import NinjaAPI
from requests_hawk import HawkAuth

hawk_auth = HawkAuth(
    id=settings.HAWK_ID,
    key=settings.HAWK_KEY,
)


def GlobalHawkAuth(request):
    return True


ninja_apis = NinjaAPI(auth=GlobalHawkAuth)
