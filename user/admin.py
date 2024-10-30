from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from simple_history import register
from simple_history.admin import SimpleHistoryAdmin

from profiles.admin import admin_site


# Register your models here.
User = get_user_model()
admin_site.unregister(Group)
admin_site.register(Group, SimpleHistoryAdmin)
admin_site.register(User, SimpleHistoryAdmin)
