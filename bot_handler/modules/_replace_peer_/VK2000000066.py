import xml.etree.ElementTree as ET

import requests

from bot_handler.core.command import Command

welcome_message = '''Добро пожаловать, зашедший! 
Ты попал в беседу анимешников группы RE:OSA! 
 
В нашем чате есть правила для комфортного проведения времени и общения для всех участников, найти их можно тут: https://vk.com/@re_osa-chat-rule 
 
Приятного общения!'''


# welcome_message = None

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


@Command('usual_message', block='defaults', disable_parser=True)
def usual_message(CurrentUse):
    event_p = CurrentUse.event_p
    if event_p['attachments'] and event_p['attachments'][0]['type'] == 'audio_message':
        try:
            curtext = mp3link_to_text(event_p['attachments'][0]['audio_message']['link_mp3'])
        except BaseException:
            return None
        payload = {
            'user_ids': CurrentUse.from_id,
            'fields': '',
            'name_case': 'Nom'
        }
        try:
            resp = CurrentUse.vk_group.api.method('users.get', payload)[0]
            text = '{} {}:\n{}'.format(resp['first_name'], resp['last_name'], curtext)
        except:
            return None
        return text


@Command('help', block='defaults', disable_parser=True)
def help(CurrentUse):
    return 'Я много чего умею, но вам не расскажу)))))))))'


@Command('chat_invite_user_by_link', block='_ACTIONS_', disable_parser=True)
def chat_invite_user_by_link(CurrentUse):
    return welcome_message


@Command('chat_invite_user', block='_ACTIONS_', disable_parser=True)
def chat_invite_user(CurrentUse):
    return welcome_message
