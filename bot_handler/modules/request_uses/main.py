import json
import random
import re
import uuid

import telebot.types
import vk_api
from telebot import apihelper

from bot_handler import CONFIG
from bot_handler.core.command import Command
from bot_handler.models import User
from global_config import TG_MY_ID
from lib.Notifier import notify
from ._config import PRICES, PAYMENT_VALID_TIME
from .utils import sberb

MODES_STRS = {
    'm': 'manual',
    'a': 'auto'
}


@Command('реквест', block='bk',
         description='Запрос юзов',
         hidden=True)
def request_uses(CurrentUse):
    if CurrentUse.parser_p.a:
        cur_mode = 'a'
    else:
        cur_mode = 'm'
    result_price = 0
    result_cmds = {}
    for item in CurrentUse.parser_p.items:
        item_info = re.match('([а-яА-Яa-zA-Z\-_]+)([0-9]+)', item)
        if not item_info:
            CurrentUse.cancel_use()
            return 'Wrong item <{}>'.format(item)
        name = item_info[1]
        count = int(item_info[2])
        if count < 1:
            CurrentUse.cancel_use()
            return 'Wrong item <{}> (<0)'.format(item)

        if name not in PRICES.keys():
            CurrentUse.cancel_use()
            return "Unknown item <{}>".format(name)

        if 'mode' in PRICES[name]:
            if cur_mode not in PRICES[name]['mode']:
                cur_modes_strs = ', '.join(['"{}"'.format(MODES_STRS[mm]) for mm in PRICES[name]['mode']])
                CurrentUse.cancel_use()
                return '<{}> can be requested only in {} mode'.format(name, cur_modes_strs)

        result_price += PRICES[name]['price'] * count
        for cmd_name, cmd_count in PRICES[name]['contains']:
            if cmd_name not in result_cmds:
                result_cmds[cmd_name] = 0
            result_cmds[cmd_name] += cmd_count * count
    if not result_cmds:
        CurrentUse.cancel_use()
        return 'Эм а кто будет команды писать и всё такое'

    request_id = str(uuid.uuid4())

    if CurrentUse.user.vk_id:

        payload = {
            'user_ids': CurrentUse.user.vk_id,
            'fields': '',
            'name_case': 'Nom'
        }
        try:
            resp = CurrentUse.vk_group.api.method('users.get', payload)[0]
            user_inf = '{} {}'.format(resp['first_name'], resp['last_name'])
        except:
            user_inf = 'TG{}'.format(CurrentUse.user.tg_id)
    else:
        user_inf = 'TG{}'.format(CurrentUse.user.tg_id)

    comment = ' '.join(CurrentUse.parser_p.comment)

    cmds_string = '\n'.join(['{} {}'.format(cmd_name, cmd_count) for cmd_name, cmd_count in result_cmds.items()])

    text = '''{}:
{}
{}
Amount: {} ₽.

{}'''.format(user_inf, cmds_string, comment, result_price, request_id)

    cur_request = {
        'user': CurrentUse.user.id,
        'items': result_cmds,
        'user_inf': user_inf,
        'contact': {'where': CurrentUse.messenger.name, 'id': CurrentUse.peer_id},
        'comment': comment,
        'amount': result_price,
        'auto': False,
    }

    if CurrentUse.parser_p.a:
        cur_request['auto'] = True
        cur_amount = result_price
        u_storage = CurrentUse.storage('u', name='sberb_user')

        if ('cards' not in u_storage) or (not u_storage['cards']):
            return 'У тя не привязано ни одной карты. Для привязки юзай /реквест.п'

        cards = u_storage['cards']

        g_storage = CurrentUse.storage('', name='sberb_global')

        CurrentUse.send_msg('Погоди немного...')
        operation = sberb.check_transaction(g_storage, cur_amount, minuts=PAYMENT_VALID_TIME, cards=cards)

        if operation is None:
            return 'Не найдено(Если сделалб все всерно, подожди пару минут и попробуй еще раз. Если трабл не пофиксился, кидай обычный реквест)'
        else:
            cur_request['accepted'] = 1
            used_transactions = g_storage['used_transactions']
            used_transactions.append(operation['id'])
            g_storage.save()

            for cmd_name, cmd_cnt in result_cmds.items():
                status = CurrentUse.user.change_executions(cmd_name, cmd_cnt)

            requst_finish(request_id, cur_request, auto=True)
            return None

    accept_payload = json.dumps({"cmd_str": "/req.r {} {}".format(request_id, 1)})
    reject_payload = json.dumps({"cmd_str": "/req.r {} {}".format(request_id, 0)})

    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    accept_btn = telebot.types.InlineKeyboardButton('Accept', callback_data=accept_payload)
    reject_btn = telebot.types.InlineKeyboardButton('Reject', callback_data=reject_payload)
    markup.add(accept_btn, reject_btn)
    resp = apihelper.send_message(CONFIG.TG_BOT_TOKEN, TG_MY_ID, text, reply_markup=markup)
    msg_id = resp['message_id']

    cur_request['msg_id'] = msg_id

    storage = CurrentUse.storage('', name='uses_requests')

    if 'actual' not in storage:
        storage['actual'] = {}

    storage['actual'][request_id] = cur_request

    storage.save()

    return 'Request has been sent.\n\n{}'.format(request_id)


parser = request_uses.parser
parser.add_argument('items', type=str, help='e.g фрифри1 ебалы2', nargs='*', default=[])
parser.add_argument('-с', dest='comment', type=str, default=[], nargs='*')
parser.add_argument('-а', dest='a', action='store_true', default=False, help='Auto accept')


@Command('req.r', block='bk',
         hidden=True)
def resp_request(CurrentUse):
    storage = CurrentUse.storage('', name='uses_requests')

    if 'actual' not in storage:
        storage['actual'] = {}

    if 'archive' not in storage:
        storage['archive'] = {}

    request_id = CurrentUse.parser_p.request_id
    accept = CurrentUse.parser_p.accept
    actual_requests = storage['actual']
    archive_requests = storage['archive']

    if request_id not in actual_requests.keys():
        if request_id in archive_requests.keys():
            CurrentUse.answer_callback_query('This request has already been processed.')
        else:
            CurrentUse.answer_callback_query('Request not found')

        return None

    req = actual_requests.pop(request_id)
    # archive_requests[request_id] = req

    if not accept:
        req['accepted'] = 0
        storage.save()
        CurrentUse.answer_callback_query('Request rejected')
        requst_finish(request_id, req)
        return None

    req['accepted'] = 1
    storage.save()

    user_id = req['user']
    user, is_new = User.objects.get_or_create(id=user_id)

    for cmd_name, cmd_cnt in req['items'].items():
        status = user.change_executions(cmd_name, cmd_cnt)

    CurrentUse.answer_callback_query('Request accepted')
    requst_finish(request_id, req)

    return None


parser = resp_request.parser
parser.add_argument('request_id', type=str)
parser.add_argument('accept', type=int)


@Command('реквест.п', block='bk', hidden=True)
def autorequest_configure(CurrentUse):
    money = 0.02
    max_cards = 3
    card_latest_digits = CurrentUse.parser_p.card_latest_digits

    if card_latest_digits is None:
        return '''1)Отправь ровно {} даньку на сбер
2)Через минуты 2 после этого (но не позже, чем через {}) напиши боту \n/реквест.п 1234\n где вместо "1234" 4 последние цифры карты, с которой были отправлены 2 копейки
3)Если все сделано верно, то эта карта будет добавлена в список твоих; При последующих автореквестах будут чекаться переводы с каждой из твоих карт

P.S: Нельзя добавить больше {} карт'''.format(money, PAYMENT_VALID_TIME, max_cards)

    if not card_latest_digits.isdigit() or len(card_latest_digits) != 4:
        return 'Чето ты со вводом 4 циферок попутал фраерок'

    g_storage = CurrentUse.storage('', name='sberb_global')
    u_storage = CurrentUse.storage('u', name='sberb_user')

    if 'cards' not in u_storage:
        u_storage['cards'] = []

    user_cards = u_storage['cards']
    if len(user_cards) >= max_cards:
        return 'У тя добавлено максимальо возможное ко-во карт.'

    CurrentUse.send_msg('Погоди немного...')
    try:
        operation = sberb.check_transaction(g_storage, money, minuts=PAYMENT_VALID_TIME,
                                            card_latest_digits=card_latest_digits)
    except Exception as exc:
        notify(exc)
        return exc

    if operation is None:
        return 'Не найдено(Если сделалб все всерно, подожди пару минут и попробуй еще раз.)'

    used_transactions = g_storage['used_transactions']

    # todo auto clear sometimes
    used_transactions.append(operation['id'])
    g_storage.save()

    cur_card = {'number': operation['from_card'], 'fio': operation['from_user'], 'op_id': operation['id']}
    user_cards.append(cur_card)
    u_storage.save()

    return 'Карта успешно добавлена'


parser = autorequest_configure.parser
parser.add_argument('card_latest_digits', type=str, nargs='?', default=None)


@Command('варики', block='bk', description='СпИсОк ПоКуПоК', hidden=True, allow_default=True)
def variants_list(CurrentUse):
    resp_text = ''
    for name, datas in PRICES.items():
        if 'hidden' in datas and datas['hidden']:
            if not CurrentUse.user.is_admin or CurrentUse.in_conversation:
                continue

        contains_str = '\n'.join(['{} {}'.format(cmd_name, cmd_count) for cmd_name, cmd_count in datas['contains']])
        if 'mode' in datas:
            mode_str = ', '.join(['"{}"'.format(MODES_STRS[mm]) for mm in datas['mode']])
            mode_str = '(only {})'.format(mode_str)
        else:
            mode_str = ''

        cur_str = '{} [{} ₽] {}:\n{}'.format(name, datas['price'], mode_str, contains_str)
        resp_text += cur_str + '\n\n'
    return resp_text


def requst_finish(req_id, req_data, auto=False):
    markup = telebot.types.InlineKeyboardMarkup()

    if req_data['accepted']:
        status = 'Accepted ✅'
    else:
        status = 'Rejected ❌'

    cmds_string = '\n'.join(['{} {}'.format(cmd_name, cmd_count) for cmd_name, cmd_count in req_data['items'].items()])

    text = '''{}:
{}
Amount: {} ₽.

{}
({})'''.format(req_data['user_inf'], cmds_string, req_data['amount'], req_id, status)

    try:
        if not auto:
            apihelper.edit_message_text(CONFIG.TG_BOT_TOKEN, text, TG_MY_ID, req_data['msg_id'], reply_markup=markup)
        else:
            # storage = CurrentUse.storage('', name='uses_requests')
            apihelper.send_message(CONFIG.TG_BOT_TOKEN, TG_MY_ID, text)
    except:
        pass

    if req_data['accepted']:
        text = 'Your request has been accepted ✅.\n'
    else:
        text = 'Your request has been rejected ❌.\n'

    text += '{}\n{}\n\n{}'.format(cmds_string, req_data['comment'], req_id)

    contact = req_data['contact']

    # todo notify user func
    if contact['where'] == 'VK':
        try:
            payload = {
                'peer_id': contact['id'],
                'random_id': random.randint(0, 10000000),
                'message': text
            }
            vk_session = vk_api.VkApi(token=CONFIG.VK_GROUP_TOKEN)
            resp = vk_session.method('messages.send', payload)
        except:
            pass
    elif contact['where'] == 'TG':
        try:
            apihelper.send_message(CONFIG.TG_BOT_TOKEN, contact['id'], text)
        except:
            pass

    return 1

# todo keyboard abstraction
# todo use Message obj to send messages
