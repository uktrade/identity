import mimetypes

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import HttpResponse, render
from django.views.decorators.csrf import csrf_exempt

from core import services
from core.api.peoplefinder.profile import upload_profile_photo
from profiles.models.peoplefinder import PeopleFinderProfile


# @login_required
@csrf_exempt
def get_profile_photo(request, slug: str):
    if request.method == "POST":
        return upload_profile_photo(request, slug)

    try:
        profile = services.get_peoplefinder_profile_by_slug(slug=slug)
    except PeopleFinderProfile.DoesNotExist:
        raise Http404()

    if not bool(profile.photo):
        return HttpResponse("")

    image = profile.photo.open()
    response = HttpResponse(content=image)
    response["Content-Type"] = str(mimetypes.guess_type(image.url)[0])
    response["Content-Length"] = image.size
    return response


def trigger_error(request):
    division_by_zero = 1 / 0
