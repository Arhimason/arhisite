import base64
import json
import os
import random
import subprocess
import sys
import time

import django
import requests
from jconfig.base import BaseConfig
from python3_anticaptcha import ImageToTextTask

import global_config
from lib.Tools import get_exc_info

abspath = os.path.abspath(__file__)
antikick_dir = os.path.dirname(abspath)

BASE_DIR = os.path.dirname(antikick_dir)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arhisite.settings')
django.setup()

from vk_antikick.models import Chat, Bot
from lib.Tools import ExecuteStack, already_running
from lib.Tools import VkApi2 as VkApi

# todo settings in database
CHECK_TIMEOUT = 1
PID_FILE = antikick_dir + '/pid.txt'


# need to fix memory leak in vk_api
class Config(BaseConfig):
    __slots__ = ('_filename',)

    def __init__(self, section, filename='.jconfig'):
        self._filename = filename

        super(Config, self).__init__(section, filename=filename)

    def load(self, filename, **kwargs):
        return {}

    def save(self):
        pass


def captcha_handler(captcha):
    r = requests.get(captcha.get_url())

    encoded = base64.b64encode(r.content).decode()

    dt = ImageToTextTask.ImageToTextTask(anticaptcha_key=global_config.ANTIGATE_KEY).captcha_handler(
        captcha_base64=encoded)
    user_answer = dt['solution']['text']

    return captcha.try_again(user_answer)


def start():
    # todo use supervisor
    # r = os.system(sys.executable + ' ' + os.path.abspath(__file__) + ' &')
    s = subprocess.Popen([sys.executable, os.path.abspath(__file__)], stdout=subprocess.PIPE)
    return s.pid


def chat_list():
    chats = Chat.objects.all()

    resp = []
    for chat in chats:
        resp.append({'id': chat.id_my, 'antikick': chat.antikick})
    return resp


def deploy_bots(chat_id_my):
    bots = Bot.objects.all()

    try:
        obj = Chat.objects.get(id_my=chat_id_my)
        exists = 1
    except Chat.DoesNotExist:
        exists = 0

    if exists:
        return 0

    code = '''
    var chat_id_my = "''' + str(chat_id_my) + '''";
    var bots = [''' + ','.join([str(bot.id) for bot in bots]) + '''];
    var i = 0;
    while (i < bots.length) {
        API.messages.addChatUser({"chat_id":chat_id_my, "user_id": bots[i]}); // allbots
        i = i + 1;
    }'''

    payload = {
        'code': code,
    }
    vk_session = VkApi(token=global_config.VK_MY_TOKEN)
    try:
        resp = vk_session.method('execute', payload)
    except:
        print(get_exc_info())
        return 0
    bots_dt = {}
    for bot in bots:
        bot.latest_chat += 1
        bot.save(update_fields=['latest_chat'])
        bots_dt[bot.id] = {'access_token': bot.access_token, 'chat_id': bot.latest_chat}
        bot_session = VkApi(token=bot.access_token)
        payload = {
            'chat_id': bot.latest_chat,
            'user_id': bot.id
        }
        resp = bot_session.method('messages.removeChatUser', payload)

    chat = Chat(id_my=chat_id_my, bots_data=json.dumps(bots_dt), antikick=False)
    chat.save()
    # chats.append(chat)
    # chats = Chat.objects.all()
    return 1


def toggle(chat_id_my, enabled):
    try:
        chat = Chat.objects.get(id_my=chat_id_my)
    except Chat.DoesNotExist:
        d = deploy_bots(chat_id_my)
        if not d:
            return 0
        chat = Chat.objects.get(id_my=chat_id_my)

    if chat.antikick == bool(enabled):
        return 0

    chat.antikick = bool(enabled)
    chat.save(update_fields=['antikick'])
    return 1


def stop():
    try:
        with open(PID_FILE) as f:
            pid = f.read()
    except BaseException:
        return 0
    os.system('kill ' + pid)
    return 1


def status():
    a = already_running('vk_anti_kick', True)
    try:
        with open(PID_FILE) as f:
            pid = f.read()
        b = os.path.isdir('/proc/' + str(pid))
    except BaseException:
        b = 0

    return a, b


def _get_latest_chat_id(sess):
    code = '''
            var l_kn_id = ''' + str(0) + ''';
            var length = 33554432;

            var cur_check = 0;
            var val = 0;
            var a = 0;
            var toret = [];
            var counter = 0;

            var min = l_kn_id;
            var max = length+l_kn_id;


            while (counter<25) {
                val = max-min;
                cur_check = min + ((val - val % 2) / 2);


                a = API.messages.getConversationsById({"peer_ids":2000000000 + cur_check});
                if (a) {
                    min = cur_check;
                } else {
                    max = cur_check;
                }
                toret = toret + [[min, max]];

                if ((max-min)<2) {
                    return min|0;
                }
                counter = counter + 1;
            }
            '''
    payload = {
        'code': code
    }
    try:
        resp = sess.method('execute', payload)
        return resp
    except:
        return None


def update_bots_info():
    bots = Bot.objects.all()
    log = ""

    for bot in bots:
        sess = VkApi(token=bot.access_token)
        pid = _get_latest_chat_id(sess)

        if pid is None:
            log += '{} deleted\n'.format(bot.id)
            bot.delete()
            continue

        if bot.latest_chat != pid:
            log += '{} {}->{}\n'.format(bot.id, bot.latest_chat, pid)
            bot.latest_chat = pid
            bot.save()

    return log


def add_bot(login, password, token=None):
    login = str(login)
    if not token:
        cbot_sess = VkApi(login=login, password=password, captcha_handler=captcha_handler)
        try:
            resp = cbot_sess.auth(token_only=True)
            token = cbot_sess.token['access_token']
            user_id = cbot_sess.token['user_id']
        except:
            return 0
    else:
        cbot_sess = VkApi(token=token)
        try:
            user_id = cbot_sess.method('users.get', {})[0]['id']
        except:
            return 0

    pid = _get_latest_chat_id(cbot_sess)
    if pid is None:
        return 0

    cbot_exec_stack = ExecuteStack(cbot_sess)
    cbot_exec_stack.add('friends.add', {'user_id': global_config.VK_MY_ID})

    for bot in Bot.objects.all():
        cbot_exec_stack.add('friends.add', {'user_id': bot.id})

        bot_sess = VkApi(token=bot.access_token, captcha_handler=captcha_handler)
        bot_sess.method('friends.add', {'user_id': user_id}, raw=True)

    my_sess = VkApi(token=global_config.VK_MY_TOKEN, captcha_handler=captcha_handler)
    my_sess.method('friends.add', {'user_id': user_id}, raw=True)

    resps = cbot_exec_stack.finish()

    Bot.objects.create(id=user_id, access_token=token, latest_chat=pid)
    return user_id


def worker():
    # todo async
    if already_running('vk_anti_kick'):
        exit('already running')

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    chats = Chat.objects.all()

    while 1:
        actions = {}
        chats_inf = {}
        for chat in chats:
            if not chat.antikick:
                continue

            cur_bots = json.loads(chat.bots_data)

            if chat.id_my not in chats_inf:
                chats_inf[chat.id_my] = {'kicked': [], 'alright': [], 'bots': cur_bots}

            if global_config.VK_MY_ID not in actions:
                cur_session = VkApi(token=global_config.VK_MY_TOKEN)
                actions[global_config.VK_MY_ID] = ExecuteStack(cur_session)

            payload = {
                "chat_id": chat.id_my
            }
            actions[global_config.VK_MY_ID].add('messages.getChat', payload, chat.id_my)
            for bot_id, bot_data in cur_bots.items():
                if bot_id not in actions:
                    cur_session = VkApi(token=bot_data['access_token'], config=Config, config_filename='1.fek')
                    actions[bot_id] = ExecuteStack(cur_session)
                payload = {
                    "chat_id": bot_data['chat_id']
                }
                actions[bot_id].add('messages.getChat', payload, chat.id_my)

        for user, execute_stack in actions.items():
            resps = execute_stack.finish()
            for resp in resps:
                vk_resp = resp[0]
                id_my = resp[1]
                # print(vk_resp)
                try:
                    kicked = vk_resp['kicked']
                except KeyError:
                    kicked = 0
                id_local = vk_resp['id']
                if kicked:
                    chats_inf[id_my]['kicked'].append(user)
                else:
                    chats_inf[id_my]['alright'].append(user)

        for chat_id_my, chat_inf in chats_inf.items():
            if not chat_inf['kicked']: continue
            if not chat_inf['alright']: continue
            # print(chat_inf['kicked'], chat_inf['alright'])
            restorer = random.choice(chat_inf['alright'])

            if restorer != global_config.VK_MY_ID:
                restorer_chat_id = chat_inf['bots'][restorer]['chat_id']
                payload = {
                    'chat_id': restorer_chat_id,
                    'user_id': restorer,
                }
                actions[restorer].add('messages.addChatUser', payload)
            else:
                restorer_chat_id = chat_id_my

            for usr_id in chat_inf['kicked']:
                payload = {
                    'chat_id': restorer_chat_id,
                    'user_id': usr_id,

                }
                actions[restorer].add('messages.addChatUser', payload)

            if restorer != global_config.VK_MY_ID:
                payload = {
                    'chat_id': restorer_chat_id,
                    'user_id': restorer,
                }
                actions[restorer].add('messages.removeChatUser', payload)

        for execute_stack in actions.values():
            execute_stack.finish()
        # gc.collect()
        time.sleep(CHECK_TIMEOUT)


if __name__ == "__main__":
    worker()
