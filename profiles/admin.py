from django.contrib import admin

from profiles.models.generic import Email, Profile
from profiles.models.staff_sso import StaffSSOProfile, StaffSSOProfileEmail


# Register your models here.
admin.site.register(Email)
admin.site.register(StaffSSOProfile)
admin.site.register(StaffSSOProfileEmail)
admin.site.register(Profile)
