from django.urls import path

from . import api, views


app_name = "core"

urlpatterns = [
    path("profiles/slug/photo", api.people_finder.get_profile_photo, name="photo"),
    path("", views.index, name="index"),
    path("sentry-debug/", views.trigger_error),
]
