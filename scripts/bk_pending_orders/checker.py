import http.client
import json
import os
import random
import sys
import time

import django
import vk_api
from telebot import apihelper

max_time = 60 * 60 * 3
# todo global bk version
ver = "3.2.2_731"

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_DIR = '/home/ec2-user/arhisite'
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arhisite.settings')
django.setup()

from bot_handler.utils.storage import StorageC
from bot_handler import CONFIG
from lib.Notifier import notify
from lib.Tools import already_running

r = already_running('bk_pending_orders')
if r:
    exit()


def notify_user(contact, text):
    if contact['where'] == 'VK':
        try:
            payload = {
                'peer_id': contact['id'],
                'random_id': random.randint(0, 10000000),
                'message': text
            }
            vk_session = vk_api.VkApi(token=CONFIG.VK_GROUP_TOKEN)
            resp = vk_session.method('messages.send', payload)
            return 1
        except:
            return 0
    elif contact['where'] == 'TG':
        try:
            apihelper.send_message(CONFIG.TG_BOT_TOKEN, contact['id'], text)
            return 1
        except:
            return 0


pending_orders = StorageC(name='bk_pending_orders')
if 'orders' not in pending_orders:
    pending_orders['orders'] = []

# cur_order = {'time': time.time(),
#              'account': akk,
#              'contact': {'where': CurrentUse.messenger.name, 'id': CurrentUse.peer_id}
#              }

statuses = {
    1: "готовится",
    2: "хуйпаймиче(2)",
    3: "готов",
    9: "выдан",
    11: "отменен"
}

todel = []
for i in range(len(pending_orders['orders'])):
    order = pending_orders['orders'][i]
    contact = order['contact']
    time_created = order['time']
    curAccount = order['account'].split('|||')

    app_headers = {
        'x-burgerking-token': '',
        "Content-Type": "application/json; charset=UTF-8",
        "Connection": "close",
        "user-agent": "okhttp/3.11.0",
        "User-Agent": '',
        "x-burgerking-version": ver,
        "x-burgerking-platform": "android"
    }
    token = curAccount[0]
    UA = curAccount[1]
    app_headers['x-burgerking-token'] = token
    app_headers['User-Agent'] = UA

    connection = http.client.HTTPSConnection('orderapp.burgerking.ru')
    while 1:
        connection.request('POST', '/api/v1/order/getLastOrder', '', app_headers)
        response = connection.getresponse()
        try:
            resp_json = json.loads(response.read())
            break
        except json.JSONDecodeError:
            continue

    queue = resp_json['response']['queue']
    pin = resp_json['response']['pin']
    status = resp_json['response']['status']

    if (time.time() - time_created) > max_time:
        todel.append(i)
        notify('Dolgovirus\n' + json.dumps(order))
        continue

    if status == 1 or status == 2:
        continue

    todel.append(i)

    if status in statuses:
        status_text = statuses[status]
    else:
        status_text = 'завершен со статусом {}'.format(status)

    text = 'Заказ {} {} {}!'.format(queue, pin, status_text)

    st = notify_user(contact, text)

if todel:
    pending_orders.refresh_from_db()

    for i in range(len(todel) - 1, -1, -1):
        pending_orders['orders'].pop(todel[i])

    pending_orders.save()
