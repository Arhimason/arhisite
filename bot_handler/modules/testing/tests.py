import json
import os
import random
import re
import time
from subprocess import check_output

import requests
import vk_api

from bot_handler.core.command import Command
from global_config import MY_HOME_IP
from global_config import VK_MY_TOKEN
from lib.Notifier import notify

bot_community_id = 2000000044


def _proxy_check_format(proxy):
    if re.search('[0-9]{,3}\.[0-9]{,3}\.[0-9]{,3}\.[0-9]{,3}:[0-9]{,6}:(HTTP|SOCKS4|SOCKS5).*', proxy):
        return 1
    else:
        return 0


# ---------BotFunctions---------


@Command('proxy_add', disable_parser=True)
def add_proxy(CurrentUse):
    proxies_file = 'cmds/proxy.txt'

    if not _proxy_check_format(CurrentUse.text):
        return 'invalid'

    with open(proxies_file, 'a') as f:
        f.write('\n' + CurrentUse.text)

    # proxies = open(proxies_file).read().split('\n')
    # if not proxies[0]:
    #     proxies.pop(0)
    # proxies.append(CurrentUse.text)
    # proxies_dat = '\n'.join(proxies)
    # with open(proxies_file, 'w') as f:
    #     f.write(proxies_dat)
    return 1


@Command('proxy_set', disable_parser=True)
def set_proxy(CurrentUse):
    proxies_file = 'cmds/proxy.txt'

    with open(proxies_file, 'w') as f:
        f.write(CurrentUse.text)

    return 1


@Command('req', disable_parser=True)
def get_request(CurrentUse):
    proxies = {
        'https': 'http://{}:38274'.format(MY_HOME_IP),
        'http': 'http://{}:38274'.format(MY_HOME_IP),
    }

    r = requests.get('https://httpbin.org/delay/0', proxies=proxies)
    resp = r.text
    return resp


@Command('тест', cnt_func=lambda parser_p: parser_p.cnt)
def test_test(CurrentUse):
    return 'Эта команда ничего не делаетб. {} юз потратился)'.format(CurrentUse.parser_p.cnt)


parser = test_test.parser
parser.add_argument('cnt', type=int, default=1, nargs='?')


@Command('testSlep', disable_parser=True)
def answer_after_sleep(CurrentUse):
    time.sleep(10)
    response = 'Поспали 10 сек'
    return response


@Command('notify', disable_parser=True)
def notifys(CurrentUse):
    n = notify(CurrentUse.text)
    return n


@Command('coco', disable_parser=True, allow_default=True)
def screen_counter(CurrentUse):
    with open('/home/d/danixui6/screenshot-rand.cf/public_html/ajax/cnt.txt') as f:
        return f.read()


@Command('cl', disable_parser=True)
def celerrr(CurrentUse):
    stt = "ps aux -A -e"
    out = str(check_output(stt.split(' ')))

    d = out.split("\\n")
    response = stt + '\n:'
    for i in d:
        response += i + '\n'
    return response


@Command('сушняк', block='rjaki',
         disable_parser=True)
def sushnyak(CurrentUse):
    return 'сушняк для [id{}|тебя]'.format(CurrentUse.from_id)


@Command('напацанов', block='rjaki',
         disable_parser=True)
def sushnyak_rand(CurrentUse):
    payload = {
        'peer_id': CurrentUse.peer_id,
        'fields': 'first_name, last_name'
    }
    resp = CurrentUse.vk_group.api.method('messages.getConversationMembers', payload)
    user = random.choice(resp['profiles'])

    return 'сушняк для [id{}|тебя]'.format(user['id'])


@Command('таворот', block='rjaki',
         disable_parser=True)
def tavorot(CurrentUse):
    return 'каворот?'.format(CurrentUse.from_id)


@Command('subproc', disable_parser=True)
def subproc(CurrentUse):
    stt = CurrentUse.text
    out = str(check_output(stt.split(' ')))

    d = out.split("\\n")
    response = stt + ':\n\n'
    for i in d:
        response += i + '\n'
    return response


@Command('sysex', disable_parser=True)
def sysex(CurrentUse):
    e = os.system(CurrentUse.text)
    return e


@Command('deuse', cnt_func=lambda parser_p: parser_p.c)
def test_cancel_use(CurrentUse):
    r = random.randrange(0, 5)
    time.sleep(r)
    rr = random.randint(0, 1)
    # rr = 0
    if rr == 0:
        CurrentUse.cancel_use()
        return 'errorr'
    else:
        return 'success'


parser = test_cancel_use.parser
parser.add_argument('-c', type=int, default=1)


@Command('pid', disable_parser=True)
def test_pid(CurrentUse):
    pid = os.getpid()
    CurrentUse.send_msg(pid)
    time.sleep(30)
    return None


@Command('multiansw', disable_parser=True)
def multiansw(CurrentUse):
    rez = -1
    for i in range(50):
        start = time.time()
        CurrentUse.send_msg(str(i) + ' часть ' + str(rez))
        rez = time.time() - start
        time.sleep(1)
    return 'конец  ' + str(rez)


@Command('errl', )
def errlogadd(CurrentUse):
    CurrentUse.error_log_add('test1', 'test2', 'test3')
    return CurrentUse.parser_p.cnt


parser = errlogadd.parser
parser = multiansw.parser
parser.add_argument('ax_id', type=str)
parser.add_argument('cnt', type=int, default=1, nargs='?')


@Command('editmsg', disable_parser=True)
def editmsg(CurrentUse):
    msgg = CurrentUse.send_msg('Создал сообщение ')
    for i in range(5):
        time.sleep(1)
        msgg.edit('Создал сообщение ' + str(i))

    msgg.edit('[end]Создал сообщение ' + str(i))
    return 'конец'


@Command('evvl', disable_parser=True)
def evvvll(CurrentUse):
    return {'eval': CurrentUse.text, 'message': CurrentUse.text}


@Command('waiter', disable_parser=True)
def testwaiter(CurrentUse):
    msgg = CurrentUse.send_msg('Создал сообщение')
    for i in range(10):
        time.sleep(1)
        msgg.waiting()

    msgg.edit('[end]Создал сообщение ' + str(i))
    return 'конец'


name = 'waiter'


@Command('time', disable_parser=True)
def timest(CurrentUse):
    event_p = CurrentUse.event_p

    # time.sleep(5)
    response = str(time.time()) + '\n' + str(event_p['date'])
    return response


@Command('attach', block='admin_tools',
         disable_parser=True)
def attach(CurrentUse):
    attachm = CurrentUse.text

    # time.sleep(5)
    response = {'message': attachm, 'attachment': attachm, 'v': '5.101'}
    return response


@Command('тарталетка', disable_parser=True)
def tartaletka(CurrentUse):
    peer_id = 74942444
    poll_params = {
        'question': 'Тут ли олды?',
        'add_answers': ['Я кст пажилая тарталетка',
                        'Сильному и независимому Ивану привет',
                        '*уходит за сменкой',
                        '*уходит за двумя полторашками', ]
    }
    code = '''
    var poll = API.polls.create(''' + json.dumps(poll_params) + ''');
    poll = "poll"+poll.owner_id+"_"+poll.id;
    var resp = API.messages.send({"peer_id": ''' + str(peer_id) + ''', "attachment": poll, "random_id": 123321});
    return resp;
    '''
    session = vk_api.VkApi(token=VK_MY_TOKEN)

    resp = session.method('execute', {'code': code, 'v': 5.92})
    return resp
    # session.m
    # return response


@Command('клавка', disable_parser=True)
def keyyyboard(CurrentUse):
    keyb = {
        "one_time": False,
        "buttons": [
            [{
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"1\"}",
                    "label": "Red"
                },
                "color": "negative"
            },
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"cmd_str\": \"/alive\"}",
                        "label": "Green"
                    },
                    "color": "positive"
                }],
            [{
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"3\"}",
                    "label": "White"
                },
                "color": "default"
            },
                {
                    "action": {
                        "type": "text",
                        "payload": "{\"button\": \"4\"}",
                        "label": "Blue"
                    },
                    "color": "primary"
                }]
        ]
    }

    return {"keyboard": json.dumps(keyb), 'message': '111'}
    # session.m
    # return response

#
# def testAllL(message):
#     response = {"message": 'это можно вызвать только 4 раза'}
#     return response
# builtins.addCMD('testAllL', testAllL, block='tests')
#
#
# def testExcept(message):
#     response = 1/0
#     return response
# builtins.addCMD('testExcept', testExcept, block='tests')
#
#
# def testDeny(message):
#     response = {"message": 'если ты это видишь, значит вирусит или я изменил конфиги'}
#     return response
# builtins.addCMD('testDeny', testDeny, block='tests')
#
#
# def cmdInDefaults(message):
#     response = {"message": 'Тупа комманда в блоке defaults'}
#     return response
# builtins.addCMD('cmdInDefaults', cmdInDefaults, block='defaults')
