#!/usr/bin/env python3
import datetime
import os
import sys
import time

import django
import requests

from global_config import VK_MY_TOKEN

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arhisite.settings')
django.setup()
from vk_daemons.models import UserAllInf

params = (
    "first_name", "last_name", "bdate", "city", "country", "home_town", "mobile_phone", "home_phone", "skype",
    "facebook",
    "twitter", "livejournal", "instagram", "site", "status", "nickname", "domain", "relatives", "relation",
    "relation_partner", "connections", "personal", "activities", "interests", "music", "movies", "tv", "books", "games",
    "about", "quotes", "universities", "schools")
# c = UserAllInf.objects.create(id='196663888', first_name='Ilya', last_name='Zenin')
# exit()
users_set = UserAllInf.objects.all()
users_ids = users_set.values_list('id', flat=True)


def get_users_info(ids):
    # todo ExecuteStack
    if len(ids) > 1000:
        raise IOError("Too many ids(>1000)")

    data = {'user_ids': ','.join(map(str, ids)),
            'fields': 'bdate,city,country,home_town,contacts,site,status,nickname,domain,relatives,relation,connections,personal,activities,interests,music,movies,tv,books,games,about,quotes,universities,schools',
            'name_case': 'Nom',
            'access_token': VK_MY_TOKEN,
            'v': '5.85'}

    response = requests.post('https://api.vk.com/method/users.get', data=data)

    json = response.json()
    try:
        inf = json['response']
    except KeyError:
        inf = -1
    return inf


def add_users(ids, group='None'):
    if len(ids) > 1000:
        raise IOError("Too many ids(>1000)")
    users_now = get_users_info(ids)
    for user_info in users_now:
        user_info['group'] = group
        usr = UserAllInf(**user_info)
        usr.save()


for i in range(0, len(users_ids), 1000):
    users_now = get_users_info(users_ids[i:min(i + 1000, len(users_ids))])
    for user_info in users_now:
        user = users_set.get(id=user_info["id"])
        changed_fields = []
        for curparam in params:
            try:
                param = user_info[curparam]
                param = str(param)
            except KeyError:
                param = ''
            if param != user.__dict__[curparam]:
                changed_fields += [curparam]
                user.__dict__[curparam] = param

                date = datetime.datetime.now().strftime("%d.%m.%Y_%H:%M:%S")
                user.LOG += date + ' ' + curparam + '->\t' + param + '\n'
        if len(changed_fields):
            user.LOG_modified_time = time.time()
            changed_fields += ['LOG', 'LOG_modified_time']
        user.save(update_fields=changed_fields)
print('Success\n')
