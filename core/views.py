from email.policy import default
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, HttpResponse
import mimetypes

from core import services
from profiles.models import PeopleFinderProfile


def index(request):
    return render(request, "core/base.html")


# @TODO ensure request is authenticated
def get_profile_photo(request, slug: str):
    try:
        profile = services.get_peoplefinder_profile_by_slug(slug=slug)
    except PeopleFinderProfile.DoesNotExist:
        # @TODO return a non-API style error
        ...
    width = request.GET.get("w", default=None)
    height = request.GET.get("h", default=None)
    image = profile.photo.open()

    response = HttpResponse(content=image)
    response['Content-Type'] = str(mimetypes.guess_type(image.url)[0])
    response['Content-Length'] = image.size
    return response


def trigger_error(request):
    division_by_zero = 1 / 0
