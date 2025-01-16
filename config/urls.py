from django.contrib import admin
from django.urls import include, path

from core.api import main_api, people_finder_api, scim_api, sso_profile_api


urlpatterns = [
    path("api/scim/", scim_api.urls),
    path("api/sso/", sso_profile_api.urls),
    path("api/peoplefinder/", people_finder_api.urls),
    path("api/", main_api.urls),
    path("admin/", admin.site.urls),
    path("auth/", include("authbroker_client.urls")),
    path("pingdom/", include("pingdom.urls")),
    path("", include("core.urls")),
]
