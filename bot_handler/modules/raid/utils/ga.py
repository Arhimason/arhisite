import json
import random
import string
import time

import requests
from django.core.exceptions import ObjectDoesNotExist
from vk_api import VkApi

from bot_handler.models import ConnectedGroup
from global_config import DJANGO_URL
from lib.Notifier import notify

tech_account = {
    'access_token': '774d441e414ca877e6b46499cc82f173d593385f7a39196cbf0e14cfc48d32516a7c8670ea260dac2ffae',
    'id': 543029055
}

tech_accounts = [tech_account]


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def _send_startup_event(group_id, group_secret):
    account = random.choice(tech_accounts)
    sess = VkApi(token=account['access_token'])
    payload = {
        'group_id': abs(group_id)
    }
    resp = sess.method('messages.allowMessagesFromGroup', payload)

    data_json = {"type": "message_new",
                 "object": {"date": int(time.time()), "from_id": account['id'], "id": 777, "out": 0,
                            "peer_id": account['id'], "text": "/startup", "conversation_message_id": 777,
                            "fwd_messages": [], "important": False, "random_id": 0, "attachments": [],
                            "is_hidden": False}, "group_id": abs(group_id), "secret": group_secret}
    data = json.dumps(data_json)
    req = requests.post(DJANGO_URL, data=data)
    return 1


def group_add(access_token, CurrentUse=None):
    # todo get latest chat id
    need_perms = ['photos', 'docs', 'messages', 'manage', 'wall']
    sess = VkApi(token=access_token)

    try:
        perms = sess.method('groups.getTokenPermissions')
    except:
        return 0, 'Неверный токен'

    have_perms = set()
    for perm in perms['permissions']:
        have_perms.add(perm['name'])

    for perm in need_perms:
        if perm not in have_perms:
            return 0, 'Необходимые права токена: ' + ', '.join(need_perms)

    group = sess.method('groups.getById', {'fields': 'description'})[0]
    group_id = group['id']
    try:
        group_obj = ConnectedGroup.objects.get(id=-group_id)
        return 0, 'Эта группа уже есть в базе данных'
    except ObjectDoesNotExist:
        pass

    payload = {
        'group_id': group_id,
        'enabled': 1,
        'api_version': 5.87,
        'message_new': 1,
        'group_change_settings': 1,

    }
    # todo all to 0?
    try:
        result = sess.method('groups.setLongPollSettings', payload)
    except:
        result = 0
    if not result:
        return 0, 'Не удалось изменить настройки Long Poll сервера'

    payload = {
        'group_id': group_id,
        'messages': 1,
        'bots_add_to_chat': 1,
        'bots_capabilities': 1,
        'bots_start_button': 1,
        'v': 5.101
    }
    try:
        result = sess.method('groups.setSettings', payload)
    except:
        result = 0
    if not result:
        return 0, 'Не удалось включить функции бота'
    secret = randomString(16)
    owner = CurrentUse.user
    group_obj = ConnectedGroup(id=-group_id,
                               access_token=access_token,
                               secret=secret,
                               owner=owner)
    group_obj.save()
    time.sleep(1)
    r = _send_startup_event(group_id, secret)

    notify('Добавлена новая группа\nhttps://vk.com/club{}'.format(abs(group_id)))
    return 1, '1'
