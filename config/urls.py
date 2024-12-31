from django.contrib import admin
from django.urls import include, path

from authbroker_client import urls as authbroker_client_urls

from scim.api import router as scim_router
from .api import protected_apis


protected_apis.add_router("/scim/v2/Users", scim_router)

urlpatterns = [
    path("", include("core.urls")),
    path("api/", protected_apis.urls),
    path("admin/", admin.site.urls),
    path("auth/", include(authbroker_client_urls)),
    path("pingdom/", include("pingdom.urls")),
]
