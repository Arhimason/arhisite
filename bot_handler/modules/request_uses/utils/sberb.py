import json
import random
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import quote_plus

import pytz
import requests

from global_config import MY_HOME_IP
from .._sberbank_auth_data import MOBILE_SDK_DATA, AUTH_POST

myip = MY_HOME_IP
proxies = {
    'https': 'http://{}:38274'.format(myip),
    'http': 'http://{}:38274'.format(myip),
}


# todo logging everywhere
def auth():
    datetime_c = datetime.utcnow()
    dtt = datetime_c.replace(microsecond=0).isoformat() + 'Z'
    ts = round(time.time() * 1000)

    MOBILE_SDK_DATA['TIMESTAMP'] = dtt
    MOBILE_SDK_DATA['GeoLocationInfo'][0]['Timestamp'] = ts
    MOBILE_SDK_DATA['GeoLocationInfo'][0]['Longitude'] = str(
        round(45.9800788 + random.randint(-500, 500) * (10 ** -7), 7))
    MOBILE_SDK_DATA['GeoLocationInfo'][0]['Latitude'] = str(
        round(51.6110521 + random.randint(-500, 500) * (10 ** -7), 7))
    MOBILE_SDK_DATA['GeoLocationInfo'][0]['HorizontalAccuracy'] = random.randint(15, 40)

    session = requests.session()
    burp0_url = "https://online.sberbank.ru:4477/CSAMAPI/login.do?mobileSdkData=" + quote_plus(
        json.dumps(MOBILE_SDK_DATA))
    burp0_headers = {"User-Agent": "Mobile Device", "Accept-Encoding": "gzip, deflate",
                     "Content-Type": "application/x-www-form-urlencoded", "Connection": "close"}
    req = session.post(burp0_url, headers=burp0_headers, data=AUTH_POST, proxies=proxies)
    resp = req.text

    root = ET.fromstring(resp)
    try:
        token = root.find('loginData/token').text
        host = root.find('loginData/host').text
    except:
        return 0

    burp0_url = "https://{}:4477/mobile9/postCSALogin.do".format(host)
    burp0_headers = {"User-Agent": "Mobile Device", "Accept-Encoding": "gzip, deflate",
                     "Content-Type": "application/x-www-form-urlencoded", "Connection": "close"}
    burp0_data = {"token": token, "appName": "\xd1\xe1\xe5\xf0\xe1\xe0\xed\xea", "appBuildOSType": "android",
                  "appVersion": "9.0.2", "appBuildType": "RELEASE", "appFormat": "STANDALONE",
                  "deviceName": "Xiaomi_Redmi_4", "deviceType": "Redmi 4", "deviceOSType": "android",
                  "deviceOSVersion": "6.0.1"}
    req = session.post(burp0_url, headers=burp0_headers, data=burp0_data, proxies=proxies)
    resp = req.text

    cookies = session.cookies.get_dict()
    return cookies['JSESSIONID'], host


def get_income_transactions(token, host, minuts=10):
    cur_date = datetime.now(timezone.utc)  # UTC time
    cur_date = cur_date.astimezone()  # local time

    burp0_url = "https://{}:4477/mobile9/private/payments/list.do".format(host)
    burp0_cookies = {
        "JSESSIONID": token
    }
    burp0_headers = {"User-Agent": "Mobile Device",
                     "Content-Type": "application/x-www-form-urlencoded;charset=windows-1251",
                     "Accept-Encoding": "gzip, deflate", "Connection": "close"}

    five_y_ago = cur_date.replace(year=cur_date.year - 5).strftime("%d.%m.%Y")
    today = cur_date.strftime("%d.%m.%Y")
    burp0_data = {"paginationSize": "50", "paginationOffset": "0", "from": five_y_ago, "to": today,
                  "includeUfs": "true", "showExternal": "true"}

    req = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=burp0_data, proxies=proxies)
    resp = req.text

    root = ET.fromstring(resp)

    status = int(root.find('status/code').text)

    if status != 0:
        raise Exception(status)

    operations = root.find('operations')
    toret = []

    for operation in operations:
        idd = operation.find('id').text
        op_date = operation.find('date').text
        from_user = operation.find('to').text
        description = operation.find('description').text

        amount = operation.find('operationAmount/amount').text
        currency = operation.find('operationAmount/currency/code').text

        try:
            from_card = operation.find('from').text
        except:
            continue

        cur_operation = {
            'id': int(idd),
            'from_card': from_card,
            'from_user': from_user,
            'date': op_date,
            'description': description,
            'amount': float(amount),
            'currency': currency
        }
        # print(cur_operation)

        if currency != 'RUB':
            continue

        if description != 'Входящий перевод':
            continue

        op_date = datetime.strptime(op_date, "%d.%m.%YT%H:%M:%S")
        op_date = pytz.timezone('Europe/Moscow').localize(op_date)
        op_date = op_date.astimezone()

        difference = cur_date - op_date
        seconds_diff = difference.total_seconds()
        if seconds_diff > minuts * 60:
            continue
        # date = date.isoformat()

        toret.append(cur_operation)
    return toret


def check_transaction(g_storage, amount_need, minuts=10, cards=None, card_latest_digits=None):
    if (cards is None) and (card_latest_digits) is None:
        raise Exception('No cards passed')

    amount_need = float(amount_need)

    if 'token' not in g_storage:
        token, host = auth()
        g_storage['token'] = token
        g_storage['host'] = host
        g_storage.save()

    token = g_storage['token']
    host = g_storage['host']

    try:
        trnss = get_income_transactions(token, host, minuts)
    except Exception as exc:
        if exc.args[0] == 3:
            token, host = auth()
            g_storage['token'] = token
            g_storage['host'] = host
            g_storage.save()
            trnss = get_income_transactions(token, host, minuts)
        else:
            print(exc)
            raise Exception("Неизвестная ошибка, не пробуй снова, розробнику отправилось уведомление")

    g_storage.refresh_from_db()
    if 'used_transactions' not in g_storage:
        g_storage['used_transactions'] = []
    used_transactions = g_storage['used_transactions']

    for operation in trnss:
        idd = operation['id']
        from_card = operation['from_card']
        from_user = operation['from_user']
        amount = operation['amount']

        if amount != amount_need:
            continue

        if idd in used_transactions:
            continue

        if card_latest_digits:
            cur_latest_d = from_card.split(' ')[-1]
            if card_latest_digits != cur_latest_d:
                continue
        elif cards:
            good = 0
            for card in cards:
                c_number = card['number']
                if c_number == from_card:
                    good = 1
                    break

            if not good:
                continue

        return operation

    return None
