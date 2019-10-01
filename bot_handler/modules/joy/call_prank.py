import hashlib
import json
import random
from urllib.parse import quote_plus

import requests

from bot_handler.core.command import Command


def send_call_prek(number, content_id):
    SEAL = 'bb6fff6d9215791e9a527cfc4b741b8c'
    attempts = 0
    while 1:
        data = {
            "action": "auth",
            "data": {
                "appname": "vc",
                "device": "android",
                "ds": 0,
                "os": "android",
                "params": {
                    "all": 0,
                    "day": 0,
                    "hours": 0,
                    "minutes": 0,
                    "month": 0,
                    "isRate": False,
                    "set_real_phone": 0,
                    "tzOffcet": 0,
                    "year": 0
                },
                "udid": ''.join(random.choices('0123456789abcdef', k=16)),
                "version": "3.3.17"
            }
        }
        burp0_url = "http://shub.voicecards.ru:80/api/iphone/new/?data=" + quote_plus(json.dumps(data))
        burp0_headers = {"Connection": "close", "Accept-Encoding": "gzip, deflate", "User-Agent": "okhttp/2.6.0"}
        req = requests.get(burp0_url, headers=burp0_headers)
        resp = req.json()
        try:
            user_id = resp['data']['userId']
            break
        except BaseException:
            attempts += 1
            if attempts == 10:
                return 0

    data = {
        "action": "order",
        "data": {
            "appname": "vc",
            "device": "android",
            "ds": 0,
            "os": "android",
            "params": {
                "action": "process",
                "all": 0,
                "contentId": str(content_id),
                "day": 0,
                "hours": 0,
                "minutes": 0,
                "month": 0,
                "phone": str(number),
                "isRate": False,
                "set_real_phone": 0,
                "sendSignature": "off",
                "sendTime": "sendNow",
                "tzOffcet": 0,
                "year": 0
            },
            "userId": user_id,
            "version": "3.4.1"
        }
    }
    data['data']['seal'] = hashlib.md5((SEAL + user_id).encode('utf-8')).hexdigest()

    burp0_url = "http://shub.voicecards.ru:80/api/iphone/new/?data=" + quote_plus(json.dumps(data))
    burp0_headers = {"Connection": "close", "Accept-Encoding": "gzip, deflate", "User-Agent": "okhttp/2.6.0"}
    req = requests.get(burp0_url, headers=burp0_headers)
    resp = req.json()
    print(resp)
    try:
        state = resp['result']['state']
    except BaseException:
        return 0

    if state != 'SUCCESS':
        return 0

    return 1


@Command('call', block='call_prek')
def call_send(CurrentUse):
    resptext = ''
    if len(CurrentUse.parser_p.phones) != 1:
        if (not CurrentUse.user.is_admin) and (int(CurrentUse.from_id) != 501398097):
            return 'ХАХАХАХ ПОШЕЛ ТЫ НАХУЙ ДУМАЛ Я БЛЯ ОСТАВЛЮ ВИРУС ТАКОЙ?))) ЮЗ КСТ ПРОЕБАЛ ДА'

    for phone in CurrentUse.parser_p.phones:
        res = send_call_prek(phone, CurrentUse.parser_p.content_id)
        resptext += '{}: {}\n'.format(phone, res)
    return resptext


parser = call_send.parser
parser.add_argument('content_id', type=int, )
parser.add_argument('phones', type=int, nargs='*')


@Command('call.c', block='call_prek', disable_parser=True, allow_default=True)
def call_categ(CurrentUse):
    if CurrentUse.text:
        idd = CurrentUse.text
    else:
        idd = "80398"
    resptext = ''
    data = {
        "action": "content",
        "data": {
            "appname": "vc",
            "device": "android",
            "ds": 0,
            "os": "android",
            "params": {
                "all": 0,
                "day": 0,
                "hours": 0,
                "id": idd,
                "minutes": 0,
                "month": 0,
                "isRate": False,
                "set_real_phone": 0,
                "type": "genre",
                "tzOffcet": 0,
                "year": 0
            },
            "seal": "5c5c067c71f578ea9e10eb4fb1df11b6",
            "userId": "1548333",
            "version": "3.3.17"
        }
    }

    burp0_url = "http://shub.voicecards.ru:80/api/iphone/new/?data=" + quote_plus(json.dumps(data))
    burp0_headers = {"Connection": "close", "Accept-Encoding": "gzip, deflate", "User-Agent": "okhttp/2.6.0"}
    req = requests.get(burp0_url, headers=burp0_headers)
    resp = req.json()
    for categ in resp['data']['content']:
        resptext += '{}: {}\n'.format(categ['id'], categ['name'])
    return resptext
