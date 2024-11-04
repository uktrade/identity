from django.apps import apps
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from profiles.models import (
    OracleCostCodes,
    OracleProfile,
    PeopleFinderProfile,
    PeopleFinderTeam,
)


admin_site = admin.site

# Register your models here.
admin_site.register(PeopleFinderProfile, SimpleHistoryAdmin)
admin_site.register(PeopleFinderTeam, SimpleHistoryAdmin)
admin_site.register(OracleCostCodes, SimpleHistoryAdmin)
admin_site.register(OracleProfile, SimpleHistoryAdmin)
admin_site.register(
    apps.get_model("profiles.historicalpeoplefinderprofile"), SimpleHistoryAdmin
)
admin_site.register(
    apps.get_model("profiles.historicalpeoplefinderteam"), SimpleHistoryAdmin
)
