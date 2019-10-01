import random
import sys
import time

from vk_api import VkApi

from lib.Tools import get_exc_info

SEND_TIMEOUT = 60 * 30

uid = '188376902'

smiles = '🌃⭐💫🌟✨🌠😴🌙🌛🌜💤🛏'
texts = [
    'Саня нафик иди спать, завтра блин рано вставать!!!',
    'Санька спи уже иди, завтра день весь впереди!1',
    'Эй быстрее засыпай, а не то собьёт трамвай',
    'Кто не ляжет прям щяс спать утром будет умирать)',
    'Делай sleep, пока не влип',
    'Если бодрствовать будешь и дальше не получишь удовольствия от подъёма пораньше...',
    'Встань и иди(Шучу, ложись и спи)',
    'Давай быстрей уже усни, сладкий сон во сне кусни',
    'Надо спать себя ложить чтоб с кайфам родине служить',
    'Если хочешь бодрый day, тогда спать иди скорей',
    'Я, конечно, не подстрекатель, но я бы на твоём месте пошёл прям щяс спать',
    'Спи ложись уже быстрей, пылесос семи морей'
]


def donothing(actions):
    return actions


agr_handlers = {
    0: donothing,
}

BASE_DIR = '/home/ec2-user/arhisite'
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from global_config import VK_MY_TOKEN
from lib.Notifier import notify
from jconfig import Config
from lib.Tools import ExecuteStack

storage = Config('sleeping', 'sanya.jconfig')

if storage['current_notifies'] is None:
    storage['current_notifies'] = 0

if storage['current_first'] is None:
    storage['current_first'] = 0

if storage['latest_send'] is None:
    storage['latest_send'] = 0

if time.time() - storage['current_first'] > 60 * 60 * 8:
    storage['current_first'] = 0
    storage['current_notifies'] = 0


def _gen_messages():
    text = random.choice(texts)
    text += ''.join(random.choices(smiles, k=random.randint(1, 5)))

    return [{'message': text, 'attachment': ''}]


def gen_actions():
    agr_level = storage['current_notifies']
    response = []
    messages = _gen_messages()
    for msg in messages:
        payload = {
            'peer_id': uid,
            'random_id': random.randint(0, 1000000),
        }
        payload.update(msg)
        cur_action = {'method': 'messages.send',
                      'payload': payload,
                      'callback': None}
        response.append(cur_action)
    if agr_level in agr_handlers and agr_handlers[agr_level]:
        response = agr_handlers[agr_level](response)

    return response


try:
    sess = VkApi(token=VK_MY_TOKEN)
    exec_stack = ExecuteStack(sess)
    payload = {'user_ids': uid, 'fields': 'online'}

    is_online = sess.method('users.get', payload)[0]['online']
    if is_online and (time.time() - storage['latest_send']) > SEND_TIMEOUT:
        storage['latest_send'] = time.time()
        actions = gen_actions()
        for action in actions:
            exec_stack.add(action['method'], action['payload'], additional=action['callback'])
        resps = exec_stack.finish()
        for resp, callback in resps:
            if callback:
                callback(resp)

        storage['current_notifies'] += 1
        if storage['current_notifies'] == 1:
            storage['current_first'] = time.time()
except:
    notify('sanya_sleep error\n' + get_exc_info())

storage.save()
