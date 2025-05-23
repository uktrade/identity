import json
import mimetypes
from io import BytesIO

from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.http import (
    FileResponse,
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotAllowed,
    HttpResponseNotFound,
    StreamingHttpResponse,
)
from django.shortcuts import HttpResponse, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from core import services
from core.api import do_hawk_auth
from core.schemas.peoplefinder.profile import ProfileResponse
from profiles import utils
from profiles.models.peoplefinder import PeopleFinderProfile
from profiles.services import image as img_service


class PhotoForm(forms.Form):
    image = forms.ImageField()

    def clean(self):
        cleaned_data = super().clean()
        if "image" not in cleaned_data:
            self.add_error("image", ValidationError("Not a valid image file"))
        else:
            self.validate_photo(cleaned_data["image"])
        return cleaned_data

    def validate_photo(self, image):

        if not hasattr(image, "image"):
            return

        if image.image.width < 500:
            self.add_error("image", ValidationError("Width is less than 500px"))

        if image.image.height < 500:
            self.add_error("image", ValidationError("Height is less than 500px"))

        # 8mb in bytes
        if image.size > 1024 * 1024 * 8:
            self.add_error("image", ValidationError("File size is greater than 8MB"))


@csrf_exempt
def profile_photo_handler(request: HttpRequest, slug: str):
    """
    Sends the request to the right function based on the method
    """
    if request.method == "GET":
        return get_profile_photo(request, slug)
    # POST and DELETE ought to be in the Ninja API but ninja and storages don't play nicely together
    elif request.method == "POST":
        return upload_profile_photo(request, slug)
    elif request.method == "DELETE":
        return delete_profile_photo(request, slug)

    return HttpResponseNotAllowed(["GET", "POST", "DELETE"])


@require_http_methods(["GET"])
@login_required
def get_profile_photo(request, slug: str, x: int | None = None, y: int | None = None):
    """
    Proxy endpoint to retrieve profile photo. Ensures requesting user is authenticated.
    """
    try:
        profile = services.get_peoplefinder_profile_by_slug(slug=slug)
    except PeopleFinderProfile.DoesNotExist:
        raise Http404()

    if not bool(profile.photo):
        return HttpResponse("")

    if x is None:
        image = img_service.get_main_profile_photo(slug)
    elif y is None:
        raise ValueError("If X is set Y must also be set for a custom image dimension")
    else:
        size = (x, y)
        prefix = f"{x}x{y}"
        image = utils.get_or_create_sized_image(
            original_filename=profile.photo.name, size=size, prefix=prefix
        )

    return FileResponse(image, True)


@csrf_exempt
@require_http_methods(["POST"])
def upload_profile_photo(request, slug: str):
    """
    Endpoint to upload a new profile photo for the given profile
    """
    if not do_hawk_auth(request):
        return HttpResponseForbidden()

    try:
        profile = services.get_peoplefinder_profile_by_slug(slug=slug)
    except PeopleFinderProfile.DoesNotExist:
        return HttpResponseNotFound(
            json.dumps(
                {
                    "message": "Unable to find people finder profile",
                }
            )
        )

    form = PhotoForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponseBadRequest(json.dumps(form.errors))

    profile.photo.delete()
    profile.photo = form.cleaned_data["image"]
    profile.save()
    return HttpResponse(ProfileResponse.from_orm(profile).json())


@require_http_methods(["DELETE"])
def delete_profile_photo(request, slug: str):
    """
    Endpoint to delete a profile photo for the given profile
    """
    if not do_hawk_auth(request):
        return HttpResponseForbidden()

    try:
        profile = services.get_peoplefinder_profile_by_slug(slug=slug)
    except PeopleFinderProfile.DoesNotExist:
        return HttpResponseNotFound(
            json.dumps(
                {
                    "message": "Unable to find people finder profile",
                }
            )
        )

    profile.photo.delete()
    return HttpResponse(ProfileResponse.from_orm(profile).json())


def trigger_error(request):
    division_by_zero = 1 / 0
