import builtins
import json
import re
import time
import uuid

from websocket import create_connection

from bot_handler.CONFIG import BOT_NAME_RUS

start_message = {
    "event": {
        "header": {
            "messageId": "fd504659-2312-4db3-9885-f4b08aeb3bdd",
            "name": "SynchronizeState",
            "namespace": "System"
        },
        "payload": {
            "accept_invalid_auth": True,
            "auth_token": "cc96633d-59d4-4724-94bd-f5db2f02ad13",
            "emotion": "neutral",
            "network_type": "WIFI::CONNECTED",
            "oauth_token": "AQAAAAAVelL1AAJ-IWj4gx4_Q03Ok4WWSViMM7Y",
            "platform_info": "android",
            "ps_activation_model": "phrase-spotter/ru-RU-activation-alisa-plus-yandex-0.1.8:ru-RU-activation-alisa-plus-yandex-0.1.8",
            "seamlessBufferDurationMs": "1",
            "speechkitVersion": "3.21.2",
            "speed": "1",
            "uuid": "357641e5de15da6ec07fbc710002a854",
            "vins": {
                "application": {
                    "app_id": "ru.yandex.searchplugin",
                    "app_version": "7.85",
                    "device_id": "f4e7e7d78e9a3aceea0ede39dc79aa99",
                    "os_version": "6.0.1",
                    "platform": "android",
                    "uuid": "357641e5de15da6ec07fbc710002a854"
                }
            },
            "voice": "shitova.us",
            "yandexuid": "6362818681543088358"
        }
    }
}

simple_message_template = {
    "event": {
        "header": {
            "messageId": "366f6165-9f2b-4ede-93ec-a4103f1948b2",
            "name": "TextInput",
            "namespace": "Vins"
        },
        "payload": {
            "application": {
                "client_time": "20181203T131410",
                "device_id": "f4e7e7d78e9a3aceea0ede39dc79aa99",
                "lang": "ru-RU",
                "timestamp": 0,
                "timezone": "Europe/Moscow"
            },
            "header": {
                "prev_req_id": "09dbaf81-ddf7-4b99-abaf-d277b70d8cd4",
                "request_id": "011f1a88-b894-4313-8a58-a8e2af3dc105",
                "sequence_number": 0
            },
            "oauth_token": "AQAAAAAVelL1AAJ-IWj4gx4_Q03Ok4WWSViMM7Y",
            "request": {
                "additional_options": {
                    "bass_options": {
                        # "cookies": [
                        #   "yandexuid=6362818681543088358",
                        #   "Session_id=3:1543088361.5.0.1543088361318:qFp22Q:86.1|360338165.-1.2|190978.664367.nD7mxfKnchJKbLlNjgjzhub_7LU",
                        #   "sessionid2=3:1543088361.5.0.1543088361318:qFp22Q:86.1|360338165.-1.2|190978.628536.6_OyJeLbhjPAnAvNYRp-5M-kjP0",
                        #   "L=RHJVU2cAYHdrYAJkb15qUXtEUE1ceHEMAyQ9.1543088361.13694.390624.69271f3772a7d74db7c19730541d3609",
                        #   "yandex_login=tqp",
                        #   "i=TY7IGFwsp+wnHcBz1iulls6IHRXCbVMGcCNv/XcKujXvW0ZMCixJEsKlqtbBCypb8eMgXdcB+OSk+jvy8nKSykTJ084=",
                        #   "my=YwA=",
                        #   "_csrf=uR6Ltp_lN5DycrXHONvYaQW2",
                        #   "ys=udn.cDp0cXA%3D#gpauto.51_53310394287109%3A46_03415679931641%3A100000_0%3A3%3A1543437729",
                        #   "yp=2147483647.ygu.1#1858448361.udn.cDp0cXA%3D#1543610529.gpauto.51_53310394287109%3A46_03415679931641%3A100000_0%3A3%3A1543437729#1558856434.sz.640x360x3#1543693233.szm.3:640x360:360x528"
                        # ],
                        # "filtration_level": 0,
                        # "screen_scale_factor": 3,
                        # "user_agent": "Mozilla/5.0 (Linux; Android 6.0.1; Redmi 4 Build/MMB29M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.100 Mobile Safari/537.36 YandexSearch/7.85"
                    },
                    "oauth_token": "AQAAAAAVelL1AAJ-IWj4gx4_Q03Ok4WWSViMM7Y"
                },
                "event": {
                    "name": "",
                    "text": "Кто твой создатель?",
                    "type": "text_input"
                },
                "experiments": [
                    "image_recognizer",
                    "music_recognizer",
                    "multi_tabs"
                ],
                # "location": {
                #   "accuracy": 100000,
                #   "lat": 51.53310394287109,
                #   "lon": 46.03415679931641,
                #   "recency": 350114782
                # },
                "reset_session": False,
                "voice_session": False
            }
        }
    }
}

prev_uuid = "09dbaf81-ddf7-4b99-abaf-d277b70d8cd4"
ws = create_connection("wss://voiceservices.yandex.net/uni.ws")
ws.send(json.dumps(start_message))


class allnone():
    def __getattr__(self, item):
        return None


def alisa_answer(CurrentUse):
    global simple_message_template, ws

    storage = CurrentUse.storage('upc')
    if 'prev_uuid' not in storage:
        storage['prev_uuid'] = ''
    prev_uuid = storage['prev_uuid']
    if 'sequence_number' not in storage:
        storage['sequence_number'] = 0
    sequence_number = storage['sequence_number']
    if 'time' not in storage:
        storage['time'] = time.time()
    if time.time() - storage['time'] > 20 * 60:
        sequence_number = 0
        prev_uuid = ''

    rezult_text = CurrentUse.text
    changes = [
        ['алиса', 'Ира'],
        ['яндекс', 'гугл'],
        ['архибот', 'алиса'],
        ['arhibot', 'алиса'],
        # ['бот', 'алиса'],
        # ['bot', 'алиса']
    ]
    for chch in changes:
        rezult_text = re.sub(chch[0], chch[1], rezult_text, flags=re.I)

    simple_message = simple_message_template.copy()
    simple_message['event']['header']['messageId'] = str(uuid.uuid4())
    simple_message['event']['payload']['header']['sequence_number'] = sequence_number
    simple_message['event']['payload']['header']['prev_req_id'] = prev_uuid
    cur_uuid = str(uuid.uuid4())
    simple_message['event']['payload']['header']['request_id'] = cur_uuid
    simple_message['event']['payload']['request']['event']['text'] = rezult_text
    simple_message['event']['payload']['application']['timestamp'] = str(round(time.time()))
    # simple_message['event']['payload']['application']['client_time'] = str(round(time.time()))

    try:
        ws.send(json.dumps(simple_message))
    except BaseException:
        ws = create_connection("wss://voiceservices.yandex.net/uni.ws")
        ws.send(json.dumps(start_message))
        ws.send(json.dumps(simple_message))

    try:
        resp = ws.recv()
    except BaseException:
        ws = create_connection("wss://voiceservices.yandex.net/uni.ws")
        ws.send(json.dumps(start_message))
        return alisa_answer(CurrentUse)

    resp_json = json.loads(resp)
    # print(resp_json)
    resp_text = resp_json['directive']['payload']['response']['cards'][0]['text']
    storage['sequence_number'] = sequence_number + 1
    storage['time'] = time.time()
    storage['prev_uuid'] = cur_uuid
    storage.save()

    if 'Алис' in resp_text or 'алис' in resp_text:
        resp_text = 'Я ' + BOT_NAME_RUS.upper() + ' ЕБАТЬ ТЯ В РОТ'
    elif 'компании Яндекс' in resp_text:
        resp_text = 'Меня сделал [id74942444|Arhimason]'
    elif 'Вот что я могу:' in resp_text:
        CurrentUse.text = ''
        CurrentUse.parser_p = allnone()
        builtins.cmdsList['main']['help'].run(CurrentUse)

        return None

    if resp_text == '...':
        try:
            title = resp_json['directive']['payload']['response']['cards'][0]['body']['states'][0]['blocks'][1]['title']
            title = re.search('>([^<]+)<', title)[1]
        except BaseException:
            title = ''

        try:
            text = resp_json['directive']['payload']['response']['cards'][0]['body']['states'][0]['blocks'][1]['text']
            text = re.search('>([^<]+)<', text)[1]
        except BaseException:
            text = ''

        if text:
            if title:
                resp_text = title + ' - ' + text
            else:
                resp_text = text
        elif title:
            resp_text = title
    else:
        if 'buttons' in resp_json['directive']['payload']['response']['cards'][0]:
            resp_text = 'Не понял блин'

    return resp_text
