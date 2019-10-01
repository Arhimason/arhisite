import random

import telebot
import vk_api

from bot_handler.CONFIG import VK_GROUP_TOKEN, TG_BOT_TOKEN, TG_PROXY
from global_config import VK_MY_ID, TG_MY_ID

telebot.apihelper.proxy = TG_PROXY


def vk_notify(data):
    session = vk_api.VkApi(token=VK_GROUP_TOKEN)
    if type(data) != dict:
        data = {
            'message': data
        }
    data['peer_id'] = VK_MY_ID
    data['random_id'] = random.randint(0, 10000000000)

    try:
        resp = session.method('messages.send', data)
    except:
        return 0

    return 1


# todo use messages ?
def tg_notify(data):
    try:
        resp = telebot.apihelper.send_message(TG_BOT_TOKEN, TG_MY_ID, data)
    except:
        return 0
    if 'message_id' not in resp:
        return 0
    return 1


notify_funcs = [tg_notify, vk_notify]


# notify_funcs = notify_funcs[::-1]


def notify(data):
    for func in notify_funcs:
        if func(data):
            return 1
    return 0
