from profiles.models import (
    CombinedProfile,
    Email,
    StaffSSOProfile,
    StaffSSOProfileEmail
)

from django.contrib import admin


# Register your models here.
admin.site.register(Email)
admin.site.register(StaffSSOProfile)
admin.site.register(StaffSSOProfileEmail)
admin.site.register(CombinedProfile)
