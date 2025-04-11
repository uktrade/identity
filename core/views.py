import json
import mimetypes

from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_not_required, login_required
from django.core.exceptions import ValidationError
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotAllowed,
    HttpResponseNotFound,
)
from django.shortcuts import HttpResponse, redirect, render
from django.views.decorators.csrf import csrf_exempt

from core import services
from core.api import do_hawk_auth
from core.schemas.peoplefinder.profile import ProfileResponse
from profiles.models.peoplefinder import PeopleFinderProfile


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
@login_not_required
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


def get_profile_photo(request, slug: str):
    """
    Proxy endpoint to retrieve profile photo. Ensures requesting user is authenticated.
    """
    if not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}")

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


@csrf_exempt
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
