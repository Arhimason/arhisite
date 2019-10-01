import json

from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin
)
from django.db import models
from vk_api import VkApi

from bot_handler.CONFIG import VK_GROUP_TOKEN
from bot_handler.core.messages import VKMessage, TGMessage


# todo use AbstractBaseUSer?
class User(models.Model):
    vk_id = models.IntegerField(null=True, blank=True, unique=True)
    tg_id = models.IntegerField(null=True, blank=True, unique=True)
    login = models.CharField(null=True, blank=True, unique=True, max_length=20)
    password = models.CharField(null=True, blank=True, max_length=64)
    permissions = models.TextField(default='{"cmds": {}, "blocks": {}, "groups": {"all":{}}}')
    executions = models.TextField(default='{}')
    is_admin = models.BooleanField(default=False)

    # todo what if no main group?
    def notify(self, text):
        if self.vk_id:
            vk_api = VkApi(token=VK_GROUP_TOKEN)
            msg = VKMessage(self.vk_id, text, vk_api)
            if msg.is_delivered:
                return msg
        if self.tg_id:
            msg = TGMessage(self.tg_id, text)
            if msg.is_delivered:
                return msg
        return 0

    # todo checking enough another cmd?
    def change_executions(self, cmdname, cnt, allow_negative_result=False):
        self.refresh_from_db(fields=['permissions', 'executions'])
        perms = json.loads(self.permissions)
        execs = json.loads(self.executions)

        try:
            limit = perms['cmds'][cmdname]['all_limit']
        except KeyError:
            limit = 0
        try:
            used_now = execs[cmdname]['all_executions']
        except KeyError:
            used_now = 0
        available_uses = limit - used_now

        if ((available_uses + cnt) < 0) and (not allow_negative_result):
            return 0

        if cmdname not in perms['cmds']:
            perms['cmds'][cmdname] = {"all_limit": cnt}
        else:
            if "all_limit" not in perms['cmds'][cmdname]:
                result = cnt
            else:
                result = perms['cmds'][cmdname]['all_limit'] + cnt

            perms['cmds'][cmdname]['all_limit'] = result

        self.permissions = json.dumps(perms, ensure_ascii=False)
        self.save(update_fields=['permissions'])
        return 1


class Group(models.Model):
    name = models.CharField(unique=True, max_length=20, primary_key=True)
    permissions = models.TextField(default='{"cmds": {}, "blocks": {}, "groups": {}}')


class UsageLog(models.Model):
    bot_id = models.IntegerField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    peer_id = models.IntegerField()
    messenger = models.CharField(max_length=10)
    cmd = models.CharField(max_length=20)
    request = models.TextField()
    response = models.TextField(null=True)
    traceback = models.TextField(null=True)
    dateTime = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(null=True)


class ErrorLog(models.Model):
    usage_log = models.ForeignKey(UsageLog, on_delete=models.CASCADE, null=True)
    messenger = models.CharField(max_length=10)
    action = models.CharField(max_length=30)
    request = models.TextField(null=True)
    additional = models.TextField(null=True)
    dateTime = models.DateTimeField(auto_now_add=True)


class ConnectedGroup(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    access_token = models.CharField(max_length=128, unique=True)
    secret = models.CharField(max_length=32, null=True)
    confirm_code = models.CharField(max_length=8, null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    dateTime = models.DateTimeField(auto_now_add=True)
    params = models.TextField(null=True, blank=True)
    latest_chat = models.IntegerField(null=True, blank=True)
    owner = models.ForeignKey(User, models.SET_NULL, null=True, blank=True)

    api = None

    def save(self, *args, **kwargs):
        nullable_fields = ['confirm_code', 'params', 'latest_chat', 'owner']
        for var in vars(self):
            print(var)
            if var in nullable_fields:
                if self.__dict__[var] == '':
                    self.__dict__[var] = None
        super(ConnectedGroup, self).save(*args, **kwargs)

    def initialize(self):
        self.api = VkApi(token=self.access_token)


class StorageTable(models.Model):
    name = models.CharField(max_length=30, null=True, blank=True)
    user = models.CharField(max_length=30, null=True, blank=True)
    peer = models.CharField(max_length=30, null=True, blank=True)
    cmd = models.CharField(max_length=30, null=True, blank=True)
    data = models.TextField(null=True, blank=True)  # todo postgre json field?

    def save(self, *args, **kwargs):
        nullable_fields = ['name', 'user', 'peer', 'cmd', 'data']
        for var in vars(self):
            if var in nullable_fields:
                if self.__dict__[var] == '':
                    self.__dict__[var] = None
        super(StorageTable, self).save(*args, **kwargs)
