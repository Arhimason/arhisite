from django.contrib import admin

from vk_daemons.models import UserAllInf


# admin.site.register(UserAllInf)


# Define the admin class
@admin.register(UserAllInf)
class UserAllInfAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'LOG_modified_time')
    list_filter = ('group',)
