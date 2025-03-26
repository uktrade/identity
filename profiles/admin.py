from django.contrib import admin

from profiles.models import PeopleFinderProfile
from profiles.models.combined import Profile
from profiles.models.generic import Country, Email, UkStaffLocation
from profiles.models.staff_sso import StaffSSOProfile, StaffSSOProfileEmail


@admin.display(description="Name")
def full_name_from_fields(obj):
    return f"{obj.first_name} {obj.last_name}"

@admin.display(description="Is Active", boolean=True)
def is_active_from_user(obj):
    return obj.user.is_active

class ProfileAdmin(admin.ModelAdmin):
    list_display = [full_name_from_fields, "sso_email_id", "is_active"]
    list_filter = ["is_active"]

class StaffSSOProfileAdmin(admin.ModelAdmin):
    list_display = [full_name_from_fields, "sso_email_id", is_active_from_user]
    list_filter = ["user__is_active"]

class PeoplefinderProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "slug", is_active_from_user]
    list_filter = ["user__is_active"]


admin.site.register(Profile, ProfileAdmin)
admin.site.register(StaffSSOProfile, StaffSSOProfileAdmin)
admin.site.register(PeopleFinderProfile, PeoplefinderProfileAdmin)
admin.site.register(Email)
admin.site.register(UkStaffLocation)
admin.site.register(Country)
