from django import forms
# Register your models here.
from django.contrib import admin
from prettyjson import PrettyJSONWidget

from bot_handler.models import User, Group, ErrorLog, UsageLog, StorageTable, ConnectedGroup


# admin.site.register(UserAllInf)

class UserForm(forms.ModelForm):
    # print(111)
    class Meta:
        model = User
        fields = '__all__'
        widgets = {
            'permissions': PrettyJSONWidget(),
            'executions': PrettyJSONWidget(),
        }


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('vk_id', 'permissions', 'executions', 'is_admin')
    form = UserForm
    # list_filter = ('vk_id',)


class UsageLogForm(forms.ModelForm):
    # print(111)
    class Meta:
        model = UsageLog
        fields = '__all__'
        widgets = {
            'request': PrettyJSONWidget(),
            'response': PrettyJSONWidget(),
            'comments': PrettyJSONWidget(),
        }


@admin.register(UsageLog)
class UsageLogAdmin(admin.ModelAdmin):
    list_display = ('cmd', 'request', 'response', 'dateTime')
    form = UsageLogForm
    list_filter = ('cmd',)


class ErrorLogForm(forms.ModelForm):
    # print(111)
    class Meta:
        model = ErrorLog
        fields = '__all__'
        widgets = {
            'request': PrettyJSONWidget(),
        }


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'messenger', 'additional', 'dateTime')
    form = ErrorLogForm
    list_filter = ('action',)


class GroupForm(forms.ModelForm):
    # print(111)
    class Meta:
        model = Group
        fields = '__all__'
        widgets = {
            'permissions': PrettyJSONWidget(),
        }


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'permissions')
    form = GroupForm


class StorageTableForm(forms.ModelForm):
    class Meta:
        model = StorageTable
        fields = '__all__'
        widgets = {
            'data': PrettyJSONWidget(),
        }


@admin.register(StorageTable)
class StorageTableAdmin(admin.ModelAdmin):
    list_display = ('name', 'peer', 'cmd', 'user')
    form = StorageTableForm
    list_filter = ('peer', 'cmd', 'name')


@admin.register(ConnectedGroup)
class ConnectedGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'access_token', 'is_active')
    list_filter = ('is_active',)
