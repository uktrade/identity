from django.contrib import admin

from profiles.models import PeopleFinderProfile
from profiles.models.combined import Profile
from profiles.models.generic import Country, Email, UkStaffLocation
from profiles.models.staff_sso import StaffSSOProfile, StaffSSOProfileEmail


# Register your models here.
admin.site.register(Email)
admin.site.register(StaffSSOProfile)
admin.site.register(StaffSSOProfileEmail)
admin.site.register(Profile)
admin.site.register(UkStaffLocation)
admin.site.register(Country)
admin.site.register(PeopleFinderProfile)
