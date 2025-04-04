from django.urls import path

from . import views


app_name = "core"

urlpatterns = [
    path(route="profiles/<str:slug>/photo", view=views.profile_photo_handler, name="photo"),
    path("sentry-debug/", views.trigger_error, name="sentry-debug"),
]
