import random
import re

import vk_api

from bot_handler.core.command import Command
from global_config import VK_MY_TOKEN


@Command('lsmeh', hidden=True,
         description='Злобный смех любы', disable_parser=True)
def luba_smeh(CurrentUse):
    parser_p = CurrentUse.parser_p
    event_p = CurrentUse.event_p

    datas = re.match('(c?[0-9]*)', CurrentUse.text, re.DOTALL)
    if not datas:
        return {'message': 'Cheto ne tak'}
    peer_id = datas[1]
    if peer_id[0] == 'c':
        peer_id = 2000000000 + int(peer_id[1:])
    payload = {
        'peer_id': peer_id,
        'attachment': 'doc74942444_488419856',
        'random_id': random.randint(0, 10000000)
    }
    vk_session = vk_api.VkApi(token=VK_MY_TOKEN)
    resp = vk_session.method('messages.send', payload)
    response = resp
    return response


@Command('avoice', disable_parser=True)
def add_voice(CurrentUse):
    event_p = CurrentUse.event_p
    name = CurrentUse.text
    if not name:
        return 'name not specified'
    try:
        attach = event_p['fwd_messages'][0]['attachments'][0]
        type = attach['type']
        id = attach[type]['id']
        owner_id = attach[type]['owner_id']
    except BaseException:
        return 'No source'
    try:
        access_key = '_' + attach[type]['access_key']
    except BaseException:
        access_key = ''

    doc = type + str(owner_id) + '_' + str(id) + access_key
    storage = CurrentUse.storage('', name='docs_attacher')
    storage[name] = doc
    storage.save()
    return 'Success'


@Command('dvoice', disable_parser=True)
def del_voice(CurrentUse):
    event_p = CurrentUse.event_p
    name = CurrentUse.text
    if not name:
        return 'name not specified'
    storage = CurrentUse.storage('', name='docs_attacher')
    if name not in storage:
        return 'Unknown name'

    storage.pop(name)

    storage.save()
    return 'Success'


@Command('svoice', disable_parser=True)
def send_voice(CurrentUse):
    event_p = CurrentUse.event_p
    datas = re.match('(c?[0-9]*) (.*)', CurrentUse.text, re.DOTALL)
    if not datas:
        return {'message': 'Cheto ne tak'}

    peer_id = datas[1]
    name = datas[2]

    storage = CurrentUse.storage('', name='docs_attacher')
    if name not in storage:
        return 'Unknown name. Existing:\n' + ', '.join(storage.keys())

    doc = storage[name]
    if peer_id[0] == 'c':
        peer_id = 2000000000 + int(peer_id[1:])
    payload = {
        'peer_id': peer_id,
        'attachment': doc,
        'random_id': random.randint(0, 10000000)
    }
    vk_session = vk_api.VkApi(token=VK_MY_TOKEN)
    resp = vk_session.method('messages.send', payload)
    response = resp
    return response
