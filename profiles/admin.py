from django.contrib import admin

from profiles.models import CombinedProfile, Email, StaffSSOEmail, StaffSSOProfile


# Register your models here.
admin.site.register(Email)
admin.site.register(StaffSSOProfile)
admin.site.register(StaffSSOEmail)
admin.site.register(CombinedProfile)
