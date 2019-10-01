import base64
import hashlib
import hmac
import json
import time

import requests
from Crypto.Cipher import AES

HMAC_SECRET_KEY = b'2Wq7)qkX~cp7)H|n_tc&o+:G_USN3/-uIi~>M+c ;Oq]E{t9)RC_5|lhAA_Qq%_4'

cipher_key = 'MjsDska724DI1tKFwVx/vFVnF071b7jYUbNJYqMGpSY='
gc_token = "NcHta397f6336cbd50d7314a8db001a86948daafee33d961eca85765d39d"


# todo add teg cmd
class AESCipher(object):
    def __init__(self, key):
        self.bs = 32

        self.key = base64.b64decode(key)

    def encrypt(self, raw):
        raw = self._pad(raw)
        cipher = AES.new(self.key, AES.MODE_ECB)
        return base64.b64encode(cipher.encrypt(raw)).decode()

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_ECB)
        return self._unpad(cipher.decrypt(enc)).decode('utf-8', errors='ignore')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]


def gc_get_inf(phone, mode):
    if mode == 'search':
        source = 'search'
        meth = 'search'
    elif mode == 'detail':
        source = 'detail'
        meth = 'number-detail'
    else:
        raise Exception('unknown mode')

    cipher = AESCipher(cipher_key)

    payload = {
        "phoneNumber": phone,
        "source": source,
        "token": gc_token
    }

    timestamp = str(round(time.time() * 1000))

    burp0_headers = {
        "X-App-Version": "4.2.0",
        "X-Req-Timestamp": timestamp,
        "X-Os": "android 6.0.1",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0.1; Redmi 4 MIUI/8.1.11)",
        "X-Token": gc_token,
        "X-Encrypted": "1",
        "X-Client-Device-Id": "8ad62b3d23795f5f",
        "X-Lang": "ru_RU",
        "Content-Type": "application/json; charset=utf-8",
        "Connection": "close",
        "Accept-Encoding": "gzip, deflate"
    }

    serialized_payload = json.dumps(payload)
    serialized_payload = serialized_payload.replace(' ', '')

    encrypted_data = cipher.encrypt(serialized_payload)

    signature_str = '{}-{}'.format(timestamp, serialized_payload)
    dig = hmac.new(HMAC_SECRET_KEY, msg=signature_str.encode(), digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(dig).decode()
    burp0_headers['X-Req-Signature'] = signature

    dtt = json.dumps({"data": encrypted_data})
    req = requests.post('https://pbssrv-centralevents.com:443/v2.1/' + meth, headers=burp0_headers, data=dtt,
                        verify=False)
    resp_encrypted = req.json()
    resp_encrypted = resp_encrypted['data']
    resp = cipher.decrypt(resp_encrypted)
    resp_json = json.loads(resp)

    return resp_json


def parse_tags(phone):
    search = gc_get_inf(phone, 'search')
    resp_arr = []
    try:
        profile = search['result']['profile']
        disp_name = profile['displayName']
        tag_count = profile['tagCount']
    except KeyError:
        return resp_arr

    if disp_name is not None:
        resp_arr.append(disp_name)

    if tag_count == 0:
        return resp_arr

    details = gc_get_inf(phone, 'detail')

    try:
        tags = details['result']['tags']
    except KeyError:
        return resp_arr

    for tag in tags:
        resp_arr.append(tag['tag'])

    return resp_arr
