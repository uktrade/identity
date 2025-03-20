from email.policy import default
from tkinter import Image
from django.core.exceptions import PermissionDenied
from django.http import Http404
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
        raise Http404()

    width = request.GET.get("w", default=None)
    height = request.GET.get("h", default=None)
    image = profile.photo.open()

    if width is not None or height is not None:
        raise NotImplementedError("dynamic resizing not yet supported")
        img = Image.open(profile.photo)
        original_width, original_height = img.size
        if width is not None:
            width = int(width)
            height = int((width / original_width) * original_height)
        elif height is not None:
            height = int(height)
            width = int((height / original_height) * original_width)
        image = img.resize((int(width), int(height)))

    response = HttpResponse(content=image)
    response['Content-Type'] = str(mimetypes.guess_type(image.url)[0])
    response['Content-Length'] = image.size
    return response


# @TODO ensure request is authenticated
def get_profile_photo_small(request, slug: str):
    try:
        profile = services.get_peoplefinder_profile_by_slug(slug=slug)
    except PeopleFinderProfile.DoesNotExist:
        raise Http404()

    image = profile.photo_small.open()
    response = HttpResponse(content=image)
    response['Content-Type'] = str(mimetypes.guess_type(image.url)[0])
    response['Content-Length'] = image.size
    return response


def trigger_error(request):
    division_by_zero = 1 / 0
