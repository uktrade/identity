from django.urls import path

from . import views


app_name = "core"

urlpatterns = [
    path(route="profiles/<str:slug>/photo", view=views.get_profile_photo, name="photo"),
    path(route="profiles/<str:slug>/photo/small", view=views.get_profile_photo_small, name="photo"),
    path("", views.index, name="index"),
    path("sentry-debug/", views.trigger_error),
]
