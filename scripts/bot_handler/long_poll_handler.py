#!/home/ec2-user/venv/bin/python3

import asyncio
import json
import os
import sys
import time
import traceback

import django
from aiohttp import ClientSession

# todo func to init
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_DIR = '/home/ec2-user/arhisite'
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arhisite.settings')
django.setup()

from bot_handler.models import ConnectedGroup
from global_config import DJANGO_URL
from lib.Notifier import notify
from lib.Tools import get_exc_info

GROUPS_UPD_TIME = 60 * 1

groups_list = {}
latest_groups_upd = 0


async def fetch(url, session, add_data=None, timeout=3):
    async with session.get(url, timeout=timeout) as response:
        resp = await response.read()
        return add_data, resp


async def post(url, session, data, add_data=None):
    async with session.post(url, json=data, timeout=20) as response:
        resp = await response.read()
        return add_data, resp


async def update_lp_url(group_id, client_session):
    group = groups_list[group_id]
    group['active'] = 0
    print('updating lp_url', group_id)
    req_url = 'https://api.vk.com/method/groups.getLongPollServer?group_id={id}&access_token={token}&v=5.101'.format(
        id=abs(group_id),
        token=group['access_token']
    )
    task = asyncio.ensure_future(fetch(req_url, client_session))
    resp = await asyncio.gather(task)
    add_data, resp = resp[0]

    resp = json.loads(resp)

    try:
        resp = resp['response']
        lp_url = '{server}?act=a_check&key={key}&wait=90&mode=2&ts='.format(**resp)
    except BaseException as exc:

        error = resp['error']
        error_code = error['error_code']
        if error_code == 27:
            group_obj = group['group_obj']
            group_obj.is_blocked = True
            group_obj.save(update_fields=['is_blocked'])
            groups_list.pop(group_id)
            print('Group', group_id, 'is BLOCKED :(')
            return 0

        text = '{}:{}'.format(group_id, get_exc_info())

        print(text)
        notify(text)
        lp_url = None
    if not lp_url:
        return 0
    group['ts'] = resp['ts']
    group['lp_url'] = lp_url
    group['active'] = 1
    return 1


async def group_events_broker(group_id, client_session):
    while 1:
        try:
            if group_id not in groups_list:
                return 1
            group_obj = groups_list[group_id]
            if not group_obj['lp_url']:
                task = asyncio.ensure_future(update_lp_url(group_id, client_session))
                success = (await asyncio.gather(task))[0]
                if not success:
                    continue
            url = group_obj['lp_url'] + str(group_obj['ts'])
            task = asyncio.ensure_future(fetch(url, client_session, timeout=10000))
            responses = await asyncio.gather(task)
            response = responses[0]
            fek, resp = response
            resp = json.loads(resp)
            # print(resp)
            if 'failed' in resp:
                if 'ts' in resp:
                    groups_list[group_id]['ts'] = resp['ts']
                    continue
                task = asyncio.ensure_future(update_lp_url(group_id, client_session))
                await asyncio.gather(task)
                continue
            groups_list[group_id]['ts'] = resp['ts']
            events = []
            for event in resp['updates']:
                event['secret'] = groups_list[group_id]['secret']
                events.append(event)

            asyncio.ensure_future(send_events_to_handler(events, client_session))
        except:
            exc_info = sys.exc_info()
            exc_info = str(exc_info[0]) + ', ' + str(exc_info[1]) + '\n\nTraceback:\n' + ''.join(
                traceback.format_tb(exc_info[2]))
            print(exc_info)


async def send_events_to_handler(events, client_session):
    if not events:
        return 0
    print('Sending event to django')
    tasks = []
    for event in events:
        asyncio.ensure_future(post(DJANGO_URL, client_session, event))
    return 1


def groups_update():
    global groups_list, latest_groups_upd
    new_groups = []
    print('Updating groups list...')
    groups_loc = {}
    group_objects = ConnectedGroup.objects.filter(is_active=True, is_blocked=False)
    for go in group_objects:
        groups_loc[go.id] = {
            'access_token': go.access_token,
            'lp_url': None,
            'secret': go.secret,
            'ts': 0,
            'group_obj': go,
            'active': 1,

        }
        if go.id in groups_list:
            groups_loc[go.id]['ts'] = groups_list[go.id]['ts']
            groups_loc[go.id]['lp_url'] = groups_list[go.id]['lp_url']
            groups_loc[go.id]['active'] = groups_list[go.id]['active']
        else:
            new_groups.append(go.id)
    latest_groups_upd = time.time()
    groups_list = groups_loc
    return new_groups


async def main():
    client_session = ClientSession()

    while 1:
        if (time.time() - latest_groups_upd) > GROUPS_UPD_TIME:
            new_groups = groups_update()
            tasks = []
            for group_id in new_groups:
                group_obj = groups_list[group_id]
                if not group_obj['active']:
                    continue
                # print(group_id)
                task = asyncio.ensure_future(group_events_broker(group_id, client_session))
                tasks.append(task)
            asyncio.gather(*tasks)

        await asyncio.sleep(10)


loop = asyncio.get_event_loop()
future = asyncio.ensure_future(main())
loop.run_forever()
