import random
import re
import xml.etree.ElementTree as ET

import requests
import vk_api

from bot_handler.core.command import Command
from global_config import VK_MY_TOKEN
from lib.Tools import ExecuteStack

MY_CHAT_ID = 243

welcome_message = 'Добро пожаловать'

title_protect = "Общество любителей Настолок(хейтеры qnet'a)"
nodel_pattern = '(qnet|кьюнет|кюнет|q-net|люба|кю нет|кнет|кью нет) (говн.{0,7}|дерьм.{0,7}|сос.{0,7}|.{0,5}ху[йё].{0,5}|ссан.{0,7}|фулшит|залуп.{0,7})'
nodel_pattern = None
del_pattern = None


def mp3link_to_text(link):
    req = requests.get(link)
    data = req.content
    YANDEX_API_KEY = 'd373adef-5817-40a3-850b-7a78fa0205b2'
    uuid_rnd = '3ca3c75aede37ef0966b6b864bb29303'
    url = 'https://asr.yandex.net/asr_xml?key=' + YANDEX_API_KEY + '&uuid=' + uuid_rnd + '&topic=queries&lang=ru-RU&disableAntimat=true'
    headers = {"Content-Type": 'audio/x-mpeg-3'}

    tmp = requests.post(url, headers=headers, data=data)
    root = ET.fromstring(tmp.text)
    return root[0].text


def handle_deleting(CurrentUse, text):
    delete = 0
    if nodel_pattern and (not re.search(nodel_pattern, text, re.IGNORECASE)):
        delete = 1
    if del_pattern and re.search(del_pattern, text, re.IGNORECASE):
        delete = 1

    if delete:
        try:
            mysess = vk_api.VkApi(token=VK_MY_TOKEN)
            msg_ids_str = str(CurrentUse.event_p['conversation_message_id'])
            code = 'return API.messages.delete({delete_for_all: 1, message_ids: API.messages.getByConversationMessageId({peer_id: ' + str(
                2000000000 + MY_CHAT_ID) + ', conversation_message_ids: "' + msg_ids_str + '"}).items@.id});'
            resp = mysess.method('execute', {'code': code})
            # CurrentUse.send_msg(str(resp))
        except:
            pass
    return delete


@Command('usual_message', block='defaults', disable_parser=True)
def usual_message(CurrentUse):
    event_p = CurrentUse.event_p
    sess = CurrentUse.vk_group.api
    if event_p['attachments']:
        if event_p['attachments'][0]['type'] == 'audio_message':
            try:
                curtext = mp3link_to_text(event_p['attachments'][0]['audio_message']['link_mp3'])
            except BaseException:
                return None
            is_del = handle_deleting(CurrentUse, curtext)
            if is_del:
                return None
            payload = {
                'user_ids': CurrentUse.from_id,
                'fields': '',
                'name_case': 'Nom'
            }
            try:
                resp = sess.method('users.get', payload)[0]
                text = '{} {}:\n{}'.format(resp['first_name'], resp['last_name'], curtext)
            except:
                return None
            return text
        elif event_p['attachments'][0]['type'] == 'photo':
            return None

            payload = {
                'chat_id': CurrentUse.peer_id - 2000000000,
                'title': 'джизус подонок'

            }

            sess.method('messages.editChat', payload)

            photo_url = None
            for cur_size in event_p['attachments'][0]['photo']['sizes']:
                if cur_size['type'] == 'p':
                    photo_url = cur_size['url']
                    break
            photo_data = requests.get(photo_url).content

            with open('1.jpg', 'wb') as f:
                f.write(photo_data)
            f = open('1.jpg', 'rb')

            payload = {
                'chat_id': MY_CHAT_ID,
                'crop_x': 0,
                'crop_y': 0,
                'crop_width': 200,
            }
            mysess = vk_api.VkApi(token=VK_MY_TOKEN)
            resp = mysess.method('photos.getChatUploadServer', payload)
            upload_url = resp['upload_url']

            b = requests.post(upload_url, files={'file': f}).json()
            resp = mysess.method('messages.setChatPhoto', {'file': b['response']}, raw=True)
    else:
        is_del = handle_deleting(CurrentUse, CurrentUse.text)
        if is_del:
            return None


@Command('chat_invite_user_by_link', block='_ACTIONS_', disable_parser=True)
def chat_invite_user_by_link(CurrentUse):
    return welcome_message


@Command('chat_title_update', block='_ACTIONS_', disable_parser=True)
def chat_title_update(CurrentUse):
    #
    if not title_protect:
        return None
    payload = {
        'chat_id': CurrentUse.peer_id - 2000000000,
        'title': title_protect
    }
    CurrentUse.vk_group.api.method('messages.editChat', payload)


@Command('chat_invite_user', block='_ACTIONS_', disable_parser=True)
def chat_invite_user(CurrentUse):
    return welcome_message


@Command('ихихи', disable_parser=True)
def random_ban(CurrentUse):
    payload = {
        'peer_id': CurrentUse.peer_id,
        'fields': 'first_name, last_name,is_admin',
        'v': 5.101
    }
    vk_session = CurrentUse.vk_group.api
    resp = vk_session.method('messages.getConversationMembers', payload)
    CurrentUse.send_msg(str(resp))

    no_admin = []
    for i in resp['items']:
        try:
            if not i['is_admin']:
                no_admin.append(i['member_id'])
        except:
            no_admin.append(i['member_id'])
    user_id = random.choice(no_admin)

    user = None
    for i in resp['profiles']:
        if i['id'] == user_id:
            user = i
            break

    exec_stack = ExecuteStack(vk_session)

    user_rjakerd_name = user['last_name'][:2] + user['first_name'][2:] + ' ' + user['first_name'][:2] + user[
                                                                                                            'last_name'][
                                                                                                        2:]
    payload = {
        'message': user_rjakerd_name + ' ' + 'без обид',
        'peer_id': CurrentUse.peer_id,
        'random_id': random.randint(0, 1000000000)
    }

    exec_stack.add('messages.send', payload)

    payload = {
        'chat_id': CurrentUse.peer_id - 2000000000,
        'user_id': user['id']
    }
    # vk_session.method('messages.removeChatUser', payload)
    exec_stack.add('messages.removeChatUser', payload)

    resp = exec_stack.finish()

    return None
