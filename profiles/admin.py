from profiles.models import CombinedProfile, Email, StaffSSOEmail, StaffSSOProfile

from django.contrib import admin


# Register your models here.
admin.site.register(Email)
admin.site.register(StaffSSOProfile)
admin.site.register(StaffSSOEmail)
admin.site.register(CombinedProfile)
