import hashlib
import xml.etree.ElementTree as ET

import requests

from bot_handler.core.command import Command
from bot_handler.models import User
from ._config import YANDEX_API_KEY


def mp3link_to_text(link):
    req = requests.get(link)
    data = req.content
    uuid_rnd = '3ca3c75aede37ef0966b6b864bb29303'
    url = 'https://asr.yandex.net/asr_xml?key=' + YANDEX_API_KEY + '&uuid=' + uuid_rnd + '&topic=queries&lang=ru-RU&disableAntimat=true'
    headers = {"Content-Type": 'audio/x-mpeg-3'}

    tmp = requests.post(url, headers=headers, data=data)
    root = ET.fromstring(tmp.text)
    return root[0].text


# ---------BotFunctions---------


@Command('totext', block='tools',
         description='speech to text')
def totext(CurrentUse):
    event_p = CurrentUse.event_p
    fwdmsgs = event_p['fwd_messages']

    resptext = ''
    indd = 0
    for fwdmsg in fwdmsgs:
        indd += 1
        if fwdmsg['attachments'] and fwdmsg['attachments'][0]['type'] == 'audio_message':
            try:
                curtext = mp3link_to_text(fwdmsg['attachments'][0]['audio_message']['link_mp3'])
            except:
                curtext = 'Тут либо вируснуло либо не распозналось\n'
            resptext += str(indd) + '. ' + curtext + '\n'

    return resptext


@Command('подскочитекабанчиком', block='tools',
         description='Пушнуть всех')
def pushall(CurrentUse):
    if CurrentUse.messenger.name != 'VK':
        return 'Робит ттока вкердакте...'
    phraze = 'надо обкашлять вопросики и порешать все чин чинарем '
    payload = {
        "peer_id": CurrentUse.peer_id
    }
    try:
        resp = CurrentUse.vk_group.api.method('messages.getConversationMembers', payload)
        members = resp['items']
    except:
        return 'Вируснуло'
    resptext = ''
    ind = 0
    countt = 0
    for memb in members:
        if memb['member_id'] < 0: continue
        resptext += '[id{}|{}]'.format(memb['member_id'], phraze[ind])
        ind += 1
        if ind == len(phraze):
            ind = 0
            countt += 1

    if countt == 0:
        resptext += phraze[ind:]

    return resptext


@Command('sha512', block='tools',
         description='sha512 hash')
def sha512(CurrentUse):
    return hashlib.sha512(CurrentUse.parser_p.str.encode()).hexdigest()


parser = sha512.parser
parser.add_argument('str', type=str)


@Command('id', block='tools',
         description='показует твой внутренний id в боте',
         allow_default=True)
def get_uid(CurrentUse):
    event_p = CurrentUse.event_p
    try:
        uid = event_p['fwd_messages'][0]['from_id']
        obj, is_new = User.objects.get_or_create(vk_id=uid)
        return obj.id
    except:
        return CurrentUse.user.id


@Command('кик', block='tools',
         description='кикает чела',
         disable_parser=1)
def vk_user_kick(CurrentUse):
    uid = CurrentUse.text
    if not uid.isdigit():
        payload = {
            'user_ids': CurrentUse.text,
        }
        try:
            uid = CurrentUse.vk_group.api.method('users.get', payload)[0]['id']
        except:
            return 'Не удалось получить id'

    payload = {
        'member_id': uid,
        'chat_id': CurrentUse.peer_id - 2000000000
    }

    try:
        resp = CurrentUse.vk_group.api.method('messages.removeChatUser', payload)
    except:
        return 'хз вирус'
