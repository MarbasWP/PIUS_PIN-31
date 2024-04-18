from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from rest_framework.authtoken.models import TokenProxy

from users.models import User


class UserAdmin(BaseUserAdmin):

    list_display = ('email', 'username')
    list_filter = ('email', 'username')


admin.site.register(User, UserAdmin)
admin.site.unregister(TokenProxy)
