import datetime
import inspect
import json
import os

from arhisite.settings import BASE_DIR
from bot_handler.core.command import Command
from bot_handler.models import UsageLog
from lib.Tools import ExecuteStack


@Command('show_cmds', block='admin_tools',
         description='Shows information about cmd(s)',
         epilog='Use /help to show all existing cmds')
def show_cmds(CurrentUse):
    if CurrentUse.messenger.name == 'VK':
        indent = '&#12288;&#12288;'
    else:
        indent = '  '

    cmds_list = CurrentUse.cmds_list
    parser_p = CurrentUse.parser_p
    show_all = parser_p.all_cmds
    result_cmds_list = cmds_list['main'].copy()

    peer = f'{CurrentUse.messenger.name}{CurrentUse.peer_id}'
    user = f'{CurrentUse.messenger.name}{CurrentUse.from_id}'
    if parser_p.peer:
        peer = parser_p.peer
    if parser_p.user:
        user = parser_p.user

    if peer in cmds_list['_replace_peer_']:
        result_cmds_list.update(cmds_list['_replace_peer_'][peer])
    if user in cmds_list['_replace_user_']:
        result_cmds_list.update(cmds_list['_replace_user_'][user])

    if parser_p.cmd:
        cmd = parser_p.cmd
        if cmd[0] == '/': cmd = cmd[1:]
        if cmd in result_cmds_list:
            resp_text = inspect.getsource(result_cmds_list[cmd].func)
            resp_text = resp_text.replace('    ', indent)

            if not resp_text:
                resp_text = 'None'
        else:
            resp_text = 'Unknown command'
    else:
        blocks_data = {}
        resp_text = 'Commands list:\n'
        for name, cur_cmd in result_cmds_list.items():
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


parser = show_cmds.parser
group = parser.add_mutually_exclusive_group(required=False)
group.add_argument("-c", "--cmd", help="Return full cmd's help ", action="store", type=str)
group.add_argument("-b", "--block", help="Return cmds only from selected block", action="store", type=str)
parser.add_argument("-a", "--all_cmds", help="Return also cmds without description", action="store_true")
parser.add_argument("-p", "--peer", help="Replace peer", action="store", type=str)
parser.add_argument("-u", "--user", help="Replace user", action="store", type=str)


@Command('exec', hidden=True,
         block='admin_tools',
         description='Execute python code',
         epilog='You should use ".." instead of tabulation', disable_parser=True)
def execute_string(CurrentUse):
    exec_scope = locals().copy()
    curr = CurrentUse.text.replace('..', '    ')
    exec(curr, globals(), exec_scope)

    if 'resp' in exec_scope:
        if exec_scope['resp'] is dict:
            resp = exec_scope['resp']
        elif exec_scope['resp'] is str:
            resp = exec_scope['resp']
        else:
            resp = json.dumps(exec_scope['resp'], ensure_ascii=False)
    else:
        resp = {'message': '***EXECUTED***'}

    return resp


parser = execute_string.parser
parser.add_argument('code')


@Command('restart', block='admin_tools',
         disable_parser=True
         )
def restart(CurrentUse):
    manage_path = os.path.join(BASE_DIR, 'manage.py')
    e0 = os.system(manage_path + " collectstatic --noinput")
    if CurrentUse.messenger.name == 'WEB':
        e1 = os.system('/sbin/reload gunicorn-arhisite')
        e2 = os.system('/sbin/reload daphne-arhisite')
    else:
        e2 = os.system('/sbin/reload daphne-arhisite')
        e1 = os.system('/sbin/reload gunicorn-arhisite')

    return 'Success'


#


# todo wipe default users cmd?


@Command('wipelogs', block='admin_tools', )
def wipelogs(CurrentUse):
    if CurrentUse.parser_p.a:
        objs = UsageLog.objects.all()
    else:
        objs = UsageLog.objects.exclude(dateTime__gte=datetime.date.today())

    for obj in objs:
        obj.delete()
    return 'deleted ' + str(len(objs)) + ' elements'  #


parser = wipelogs.parser
parser.add_argument('-a', action='store_true')


@Command('leave', block='admin_tools',
         hidden=True,
         description='leave chat')
def leave_chat(CurrentUse):
    lst = list(CurrentUse.parser_p.chat_ids)
    ll = len(lst)
    resp_text = ''
    execute_stack = ExecuteStack(CurrentUse.vk_group.api)
    while lst:
        chat_id = lst.pop(0)
        if chat_id > 2000000000:
            chat_id = chat_id - 2000000000

        payload = {
            'chat_id': chat_id,
            'member_id': CurrentUse.vk_community.id
        }

        execute_stack.add('messages.removeChatUser', payload, chat_id)

    responses = execute_stack.finish()
    for resp in responses:
        resp_text += str(resp[1]) + ': ' + str(resp[0]) + '\n'

    return resp_text


parser = leave_chat.parser
parser.add_argument('chat_ids', type=int, nargs='*')
