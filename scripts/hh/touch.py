#!/usr/local/bin/python3

import sys
import time

import requests

BASE_DIR = '/home/ec2-user/arhisite'
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from lib.Notifier import notify
from ._config import TOUCH_LIST

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"


def touch(item, attempts=100):
    res_id = item['res_id']
    burp0_cookies = item['cookie']
    burp0_headers = {"Connection": "close", "Origin": "https://saratov.hh.ru",
                     "User-Agent": UA,
                     "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryiEWt3RN0RLTKYqY7",
                     "Accept": "application/json", "X-Requested-With": "XMLHttpRequest",
                     "X-Xsrftoken": item['xsrftoken'], "DNT": "1",
                     "Referer": "https://saratov.hh.ru/applicant/resumes?from=header_new",
                     "Accept-Encoding": "gzip, deflate", "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"}
    burp0_data = "------WebKitFormBoundaryiEWt3RN0RLTKYqY7\r\nContent-Disposition: form-data; name=\"resume\"\r\n\r\n" + res_id + "\r\n------WebKitFormBoundaryiEWt3RN0RLTKYqY7\r\nContent-Disposition: form-data; name=\"undirectable\"\r\n\r\ntrue\r\n------WebKitFormBoundaryiEWt3RN0RLTKYqY7--\r\n"
    status = 0
    for i in range(100):
        req = requests.post("https://saratov.hh.ru:443/applicant/resumes/touch", headers=burp0_headers,
                            cookies=burp0_cookies, data=burp0_data)
        status = req.status_code
        if status == 200:
            break
        time.sleep(1)
    return status == 200


for item in TOUCH_LIST:
    status = touch(item)

    if status != 200:
        notify("Can't touch resume " + item['res_id'])
