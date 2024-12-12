from django.contrib import admin

from profiles.models import (
    CombinedProfile,
    Email,
    StaffSSOProfileEmail,
    StaffSSOProfile,
)


# Register your models here.
admin.site.register(Email)
admin.site.register(StaffSSOProfile)
admin.site.register(StaffSSOProfileEmail)
admin.site.register(CombinedProfile)
