from django import forms
from django.contrib import admin
from prettyjson import PrettyJSONWidget

from vk_antikick.models import Bot, Chat


# Register your models here.


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ('id', 'access_token')


class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = '__all__'
        widgets = {
            'bots_data': PrettyJSONWidget(),
        }


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id_my', 'antikick')
    form = ChatForm
