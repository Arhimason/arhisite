import datetime
import html
import random
import re
import time

import requests

from bot_handler.core.command import Command
from .utils.Alisa import alisa_answer

agent = {'User-Agent':
             "Mozilla/4.0 (\
             compatible;\
             MSIE 6.0;\
             Windows NT 5.1;\
             SV1;\
             .NET CLR 1.1.4322;\
             .NET CLR 2.0.50727;\
             .NET CLR 3.0.04506.30\
             )"}


def translate(to_translate, to_language="auto", from_language="auto"):
    to_translate = to_translate.replace('\n', '~')
    payload = {
        "hl": to_language,
        "sl": from_language,
        "q": to_translate,
    }
    req = requests.post('https://translate.google.com/m', data=payload)
    data = req.text
    expr = r'class="t0">(.*?)<'
    re_result = re.findall(expr, data)
    if (len(re_result) == 0):
        result = ""
    else:
        result = html.unescape(re_result[0])
    result = result.replace('~', '\n')
    result = re.sub('\[([^ ]*) \| ([^\]]*)\]', '[\g<1>|\g<2>]', result)
    return result


def troll(text):
    langcodes = ["ka", "zu", "yi", "kn", "so"]
    cnt = 2
    for i in range(cnt):
        text = translate(text, 'ru', random.choice(langcodes))
    return text


# ---------BotFunctions---------
@Command('alive', block='defaults', description='Check bot')
def alive(CurrentUse):
    vars = [
        'Кто если не я, врубись, никто другой',
        'ДАЯМАШИНА',
        'Угум',
        'ES OFCORRS',
        'Ты это мне?',
        'Неважно',
        'Я не спрашивал',
        'Было',
        'Da, I am alive blin!!1',
        'Честь имею',
        'Я живой, а ты?',
        'вам бан'
    ]

    time_ago = datetime.timedelta(seconds=time.time() - CurrentUse.start_time)

    return '{}\n Current worker restarted {} ago'.format(random.choice(vars), time_ago)


# todo show only allowed cmds
@Command('help', block='defaults', description='Shows information about cmd(s)',
         epilog='Use /help to show all existing cmds')
def show_help(CurrentUse):
    cmds_list = CurrentUse.cmds_list

    parser_p = CurrentUse.parser_p
    show_all = parser_p.all_cmds
    result_cmdsList = cmds_list['main'].copy()

    peer = f'{CurrentUse.messenger.name}{CurrentUse.peer_id}'
    user = f'{CurrentUse.messenger.name}{CurrentUse.from_id}'
    if peer in cmds_list['_replace_peer_']:
        result_cmdsList.update(cmds_list['_replace_peer_'][peer])
    if user in cmds_list['_replace_user_']:
        result_cmdsList.update(cmds_list['_replace_user_'][user])

    if parser_p.cmd:
        cmd = parser_p.cmd
        if cmd[0] == '/': cmd = cmd[1:]
        if cmd in result_cmdsList:
            resp_text = result_cmdsList[cmd].get_help()
            if not resp_text:
                resp_text = 'None'
        else:
            resp_text = 'Unknown command'
    else:
        blocks_data = {}
        resp_text = 'Commands list:\n'
        for name, cur_cmd in result_cmdsList.items():
            if cur_cmd.hidden:
                if not parser_p.block:
                    continue
            else:
                if (not cur_cmd.description) and not show_all:
                    continue

            if cur_cmd.block not in blocks_data:
                blocks_data[cur_cmd.block] = ''
            blocks_data[cur_cmd.block] += '/' + name + ' - ' + str(cur_cmd.description) + '\n'

        if parser_p.block:
            if parser_p.block not in blocks_data:
                return 'Unknown block'
            resp_text += '--------{}--------\n'.format(parser_p.block)
            resp_text += blocks_data[parser_p.block]
            resp_text += '--------{}--------\n\n'.format(parser_p.block)
        else:
            for name, block_data in blocks_data.items():
                resp_text += '--------{}--------\n'.format(name)
                resp_text += block_data
                resp_text += '--------{}--------\n\n'.format(name)

        resp_text += '---\n Use /help -c command_name for details\n'
    return resp_text


parser = show_help.parser
group = parser.add_mutually_exclusive_group(required=False)
group.add_argument("-c", "--cmd", help="Return full cmd's help ", action="store", type=str)
group.add_argument("-b", "--block", help="Return cmds only from selected block", action="store", type=str)
parser.add_argument("-a", "--all_cmds", help="Return also cmds without description", action="store_true")


@Command('tr', block='rjaki', description='Переводчик с приколом',
         epilog='Use /help to show all existing cmds', disable_parser=True)
def tr(CurrentUse):
    event_p = CurrentUse.event_p
    if event_p['fwd_messages']:
        text = ''
        for msg in event_p['fwd_messages']:
            text += msg['text'] + '\n'
    else:
        text = CurrentUse.text

    return {"message": troll(text), "forward_messages": ""}


parser = tr.parser
parser.add_argument('text')


@Command('usual_message', disable_log=True,
         block='defaults', disable_parser=True)
def usual_message(CurrentUse):
    event_p = CurrentUse.event_p

    if event_p['fwd_messages'] and (event_p['fwd_messages'][0]['from_id'] == -173027900):
        if CurrentUse.user.is_admin:
            return 'Да, хозяин'

    push_words = ['архибот',
                  'arhibot',
                  'архи',
                  'бот']
    is_nazvan = 0
    pushword = ''
    for pushword in push_words:
        is_nazvan = re.match(pushword + '[ |,].*', CurrentUse.text, re.IGNORECASE + re.DOTALL)
        if is_nazvan:
            break

    if is_nazvan:
        CurrentUse.text = re.sub('^' + pushword + '[ ,]{,3}', '', CurrentUse.text, flags=re.IGNORECASE)

    if not CurrentUse.in_conversation or CurrentUse.is_pushed or is_nazvan:
        answ = alisa_answer(CurrentUse)
        if answ is None: return None
        answ = {'message': answ, 'forward_messages': ''}
        return answ
    else:
        return None

    if (len(CurrentUse.text) > 10) and (random.randint(0, 15) == 0):
        if random.randint(0, 1) == 0:
            answ = alisa_answer(CurrentUse)
            answ = {'message': answ, 'forward_messages': ''}
            return answ
        else:
            return troll(CurrentUse.text)
    else:
        return None

# def zapili(CurrentUse):
#     storage = CurrentUse.storage('', name='zapil')
#
#     now_time = datetime.datetime.now(timezone('Europe/Saratov'))
#     now_time = now_time.strftime("%Y-%m-%d %H:%M:%S %Z")
#     cur_idea = {'date': now_time, "decription": CurrentUse.text, 'user': CurrentUse.from_id}
#
#     if 'new_ides' not in storage:
#         storage['new_ides'] = []
#     storage['new_ides'].append(cur_idea)
#     storage.save()
#     return 'Мб пажилой розробник бота когда нибудь это сделает в своем лучшем в мире боте угум'
# cur_command = Command('запили', zapili,
#                       block='defaults', description='Че крутого можно запилить в боте?', disable_parser=True)
# cur_command.add_to_list()
#
#
# def che_zapilit(CurrentUse):
#     if CurrentUse.messenger.name == 'VK':
#         indent = '&#12288;&#12288;'
#     else:
#         indent = '  '
#     storage = CurrentUse.storage('', name='zapil')
#
#     formatted_json = json.dumps(storage['new_ides'], indent=indent, ensure_ascii=False)
#
#     return formatted_json
# cur_command = Command('чезапилить', che_zapilit,
#                       block='defaults', description='Список для запила', disable_parser=True)
# cur_command.add_to_list()
