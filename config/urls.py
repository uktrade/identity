from django.contrib import admin
from django.urls import include, path

from core.api import protected_apis


urlpatterns = [
    path("", include("core.urls")),
    path("api/", protected_apis.urls),
    path("admin/", admin.site.urls),
    path("auth/", include("authbroker_client.urls")),
    path("pingdom/", include("pingdom.urls")),
]
