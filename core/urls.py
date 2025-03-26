from django.urls import path

from . import views


app_name = "core"

urlpatterns = [
    path(route="profiles/<str:slug>/photo", view=views.get_profile_photo, name="photo"),
    path("sentry-debug/", views.trigger_error, name="sentry-debug"),
]
