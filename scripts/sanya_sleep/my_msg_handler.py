import sys

# todo auto change keyboard
# todo a lot of rjakich
BASE_DIR = '/home/ec2-user/arhisite'
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import time
import random
import vk_api
import re
from global_config import VK_MY_TOKEN, VK_MY_ID

sanya_id = 188376902

timeout = 0.3

regex = re.compile('ко', re.IGNORECASE)


def get_ko_count():
    return random.randint(1, 3)


def sanya_handler(msg):
    if 'update_time' in msg:
        return 0
    if msg['from_id'] != VK_MY_ID:
        return 0
    if 'ко' in msg['text']:
        t = regex.split(msg['text'])
        for i in range(len(t) - 1):
            t[i] += 'КО' * get_ko_count()
        result = ''.join(t)
        edit_message(msg['peer_id'], msg['id'], result)


special_peer_handlers = {sanya_id: sanya_handler}

_skip_mode = 0
sess = vk_api.VkApi(token=VK_MY_TOKEN)

hist_payload = {
    'pts': 0,
    'fields': '',
    'msgs_limit': 1000,
}


def _get_latest_pts():
    payload = {
        'need_pts': 1
    }
    resp = sess.method('messages.getLongPollServer', payload)
    return resp['pts']


def send_message(user_id, data):
    if type(data) != dict:
        data = {'message': data}
    data['peer_id'] = user_id
    data['random_id'] = random.randint(0, 100000)
    resp = sess.method('messages.send', data, raw=True)

    if 'error' in resp:
        return 0

    return 1


def edit_message(peer_id, msg_id, data):
    if type(data) != dict:
        data = {'message': data}
    data['message_id'] = msg_id
    data['random_id'] = random.randint(0, 100000)
    data['peer_id'] = peer_id
    resp = sess.method('messages.edit', data, raw=True)

    if 'error' in resp:
        return 0

    return 1


def def_handle(msg):
    if 'latest' not in msg: return 0
    if msg['text'] == 'alive':
        send_message('74942444', {'message': 'да я жив'})
    return 1


cur_pts = _get_latest_pts()
while 1:
    hist_payload['pts'] = cur_pts

    try:
        resp_json = sess.method('messages.getLongPollHistory', hist_payload)
        cur_pts = resp_json['new_pts']

    except KeyError:
        print('No new_pts found\n')
        time.sleep(3)
        continue

    try:
        new_messages = resp_json['messages']['items']
    except KeyError:
        print('No msgs found\n', resp_json)
        continue
    if not new_messages:
        _skip_mode = 0

    for cur_msg_id in range(len(new_messages)):
        cur_msg = new_messages[cur_msg_id]
        if not _skip_mode:
            cur_msg['latest'] = 1

        try:
            f = special_peer_handlers[cur_msg['peer_id']]
        except BaseException:
            f = def_handle
        resp = f(cur_msg)

    # print(len(new_messages), 'msgs handled')
    time.sleep(timeout)
