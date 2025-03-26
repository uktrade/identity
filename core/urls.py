from django.urls import path

from . import views


app_name = "core"

urlpatterns = [
    path("sentry-debug/", views.trigger_error),
]
