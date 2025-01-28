from django.contrib import admin

from core.services import sync_bulk_sso_users
from user.models import User


# # Register your models here.


@admin.register(User)
class SSOSyncUserAdmin(admin.ModelAdmin):
    actions = ["sync_sso_users"]

    @admin.action(description="Sync identity users with Staff SSO")
    def sync_sso_users(self, request, queryset) -> None:
        sync_bulk_sso_users(dry_run=False)
