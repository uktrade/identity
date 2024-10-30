from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from profiles.models import (
    OracleCostCodes,
    OracleProfile,
    PeopleFinderProfile,
    PeopleFinderTeam,
)


# Register your models here.
admin.site.register(PeopleFinderProfile, SimpleHistoryAdmin)
admin.site.register(PeopleFinderTeam, SimpleHistoryAdmin)
admin.site.register(OracleCostCodes, SimpleHistoryAdmin)
admin.site.register(OracleProfile, SimpleHistoryAdmin)
