from django.contrib import admin

from profiles.models import Email, Profile, StaffSSOProfile, StaffSSOProfileEmail


# Register your models here.
admin.site.register(Email)
admin.site.register(StaffSSOProfile)
admin.site.register(StaffSSOProfileEmail)
admin.site.register(Profile)
