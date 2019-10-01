import http.client
import json
import os

import sys

sys.path.append('/home/ec2-user/arhisite')

from lib.Notifier import notify
from lib.Tools import EasyThreading

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

try:
    latest_code = int(open('latest_code.txt').read())
except:
    latest_code = None

if not latest_code:
    latest_code = 13151

ver = "3.2.2_731"
count_to_check = 1000
rest_id = 432

concurrent = 100
UA = {"id": "b9c7863f-c6d8-4254-a1a9-f4d3a3aee11b", "vendor": "Xiaomi", "model": "Redmi 4", "os": "android",
      "os_ver": "3.18.24-perf-g9e4d488", "os_api": "23"}

app_headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Connection": "close",
    "user-agent": "okhttp/3.10.0",
    "User-Agent": json.dumps(UA),
    "x-burgerking-version": ver,
    "x-burgerking-platform": "android"
}


def get_coupon(payload):
    rest_id = payload['rest_id']
    coupon_code = payload['key']
    connection = http.client.HTTPSConnection('orderapp.burgerking.ru')
    url = '/api/v1/menu/coupons?restaurant={}&code={}'.format(rest_id, coupon_code)
    connection.request('GET', url, headers=app_headers)
    response = connection.getresponse()
    status = response.status
    resp = response.read()
    # print(coupon_code, resp)
    if status == 200:
        try:
            jsonn = json.loads(resp)
        except:
            notify(resp.decode())
            jsonn = {}

        return jsonn
    elif status == 400:
        return 0
    else:
        notify(response.read().decode())
        return 0


easy_threading = EasyThreading(get_coupon, concurrent)

for i in range(latest_code + 1, latest_code + 1 + count_to_check):
    payload = {'key': i, 'rest_id': rest_id}
    easy_threading.add_payload(payload)

resps = easy_threading.finish()

for code, resp in resps.items():
    if not resp: continue
    notify(json.dumps(resp, ensure_ascii=False))
    if code > latest_code:
        latest_code = code

open('latest_code.txt', 'w').write(str(latest_code))
