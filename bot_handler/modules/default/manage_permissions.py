import collections
import json

from bot_handler.core.command import Command
from bot_handler.models import User, Group


def dict_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = dict_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


# todo refactor all!!!


@Command('perms.e', hidden=True,
         block='admin_tools',
         description='Manage permissions',
         epilog='''Allowed params:\r\nblocks: deny\n||cmds: deny, all_limit, time_limit, timeout''')
def perms_edit(CurrentUse):
    # TODO Good where
    # todo good time
    parser_p = CurrentUse.parser_p
    event_p = CurrentUse.event_p

    alowed_config_params = {'groups': [], 'blocks': ['deny', 'where'],
                            'cmds': ['deny', 'time_limit', 'all_limit', 'timeout', 'where']}
    timeouts = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800}
    params = CurrentUse.text.split(' ')
    if len(params) < 5:
        return "Wrong params count\n" + str(len(params))
    c_type = parser_p.object
    c_section = parser_p.section
    c_action = parser_p.action
    c_howtoget = parser_p.howtoget.split('=')
    c_names = parser_p.names
    try:
        c_config = json.loads(parser_p.configs[0])
    except BaseException:
        # print(sys.exc_info())
        c_config = {}
        for c in parser_p.configs:
            cc = c.split('=')
            if cc[0] == 'timeout':
                try:
                    cc[1] = int(cc[1][:-1]) * timeouts[cc[1][-1]]
                except BaseException:
                    return "Wrong params string\n" + c

            try:
                if type(cc[1]) == int or cc[1].isdigit():
                    cc[1] = int(cc[1])
                c_config[cc[0]] = cc[1]
            except BaseException:
                return "Wrong params string\n" + c
    if c_howtoget[0] == 'fwd':
        if event_p['fwd_messages']:
            uid = event_p['fwd_messages'][0]['from_id']
            c_howtoget = ['vk_id', uid]
        else:
            return "No forwarded messages"

    if c_type == 'group':
        if c_section == 'groups':
            return "Wrong action"

        try:
            obj, is_new = Group.objects.get_or_create(name=c_howtoget[0])
        except BaseException:
            return "Group <" + c_howtoget[0] + "> doesn't exist"
    elif c_type == 'user':
        try:
            obj, is_new = User.objects.get_or_create(**{c_howtoget[0]: c_howtoget[1]})
        except BaseException:
            return "User <" + '='.join(c_howtoget) + "> doesn't exist"
    else:
        return "Unknown type <" + c_type + ">"
    cur_perms = json.loads(obj.permissions)
    if c_section not in cur_perms:
        return "Unknown section <" + c_section + ">"

    for conf_param in c_config:
        if conf_param not in alowed_config_params[c_section]:
            return 'Wrong param <' + conf_param + '>'

    if c_action == 'jsetall':
        cur_perms[c_section] = c_config
        c_names = []
    elif c_action == 'setall':
        cur_perms[c_section] = {}
        c_action = 'add'

    for name in c_names:
        if c_action == 'add':
            if name in cur_perms[c_section]:
                return "<" + name + "> already exists!"
            cur_perms[c_section][name] = c_config
        elif c_action == 'del':
            if name not in cur_perms[c_section]:
                return "<" + name + ">  not found!"
            cur_perms[c_section].pop(name)
        elif c_action == 'upd':
            if name not in cur_perms[c_section]:
                return "<" + name + "> not found!"
            cur_perms[c_section][name].update(c_config)
        elif c_action == 'set':
            if name not in cur_perms[c_section]:
                return "<" + name + "> not found!"
            cur_perms[c_section][name] = c_config

    cur_perms = json.dumps(cur_perms, ensure_ascii=False)
    obj.permissions = cur_perms
    obj.save()
    return "Success!"


parser = perms_edit.parser
parser.add_argument('object', choices=['user', 'group'])
parser.add_argument('section', choices=['cmds', 'blocks', 'groups'])
parser.add_argument('action', choices=['jsetall', 'setall', 'add', 'del', 'upd', 'set'])
parser.add_argument('howtoget', help='e.g. vk_id=1')
parser.add_argument('-n', dest='names', metavar='NAME', nargs='*', default=[])
parser.add_argument('-p', dest='configs', help='or json string(WITHOUT SPACES!)', metavar='PARAM=DATA', nargs='*',
                    default={})


@Command('perms.s', hidden=True,
         block='admin_tools',
         description='Show permissions')
def perms_show(CurrentUse):
    parser_p = CurrentUse.parser_p
    event_p = CurrentUse.event_p

    c_howtoget = parser_p.howtoget.split('=')

    if c_howtoget[0] == 'fwd':
        if event_p['fwd_messages']:
            uid = event_p['fwd_messages'][0]['from_id']
            c_howtoget = ['vk_id', uid]
        else:
            return "No forwarded messages"

    if parser_p.object == 'user':
        try:
            obj = User.objects.get(**{c_howtoget[0]: c_howtoget[1]})
        except BaseException:
            return "User <" + '='.join(c_howtoget) + "> doesn't exist"
    elif parser_p.object == 'group':
        try:
            obj = Group.objects.get(name=c_howtoget[0])
        except BaseException:
            return "Group <" + c_howtoget[0] + "> doesn't exist"
    else:
        return "Virusi"

    cur_perms = json.loads(obj.permissions)
    if parser_p.show_result:
        result_perms = {}
        for groupName in cur_perms['groups']:
            try:
                cur_group = Group.objects.get(name=groupName)
            except Group.DoesNotExist:
                CurrentUse.error_log_add('Unknown group', additional=groupName)
                # print("unknown_group")
                continue
            result_perms = dict_update(result_perms, json.loads(cur_group.permissions))
        result_perms = dict_update(result_perms, cur_perms)
    else:
        result_perms = cur_perms
    formatted_json = json.dumps(result_perms, indent='____', ensure_ascii=False)
    return formatted_json


parser = perms_show.parser
parser.add_argument('object', choices=['user', 'group'])
parser.add_argument('howtoget', help='e.g. vk_id=1')
parser.add_argument('-r', dest='show_result', help='show result perms', default=False, action="store_true")


# todo good perms


@Command('perms', description='Show current user permissions',
         block='defaults')
def perms_show_my(CurrentUse):
    if CurrentUse.messenger.name == 'VK':
        indent = '&#12288;&#12288;'
    else:
        indent = '  '
    parser_p = CurrentUse.parser_p
    event_p = CurrentUse.event_p

    cur_user = CurrentUse.user
    cur_user_perms = json.loads(cur_user.permissions)
    if parser_p.show_result:
        result_perms = {}
        for groupName in cur_user_perms['groups']:
            try:
                cur_group = Group.objects.get(name=groupName)
            except Group.DoesNotExist:
                CurrentUse.error_log_add('Unknown group', additional=groupName)
                # print("unknown_group")
                continue
            result_perms = dict_update(result_perms, json.loads(cur_group.permissions))
        result_perms = dict_update(result_perms, cur_user_perms)
    else:
        result_perms = cur_user_perms
    formatted_json = json.dumps(result_perms, indent=indent, ensure_ascii=False)
    return formatted_json


parser = perms_show_my.parser
parser.add_argument('-r', dest='show_result', help='show result perms', default=False, action="store_true")


@Command('uses.e', hidden=True,
         block='admin_tools',
         description='Manage uses',
         epilog='''Allowed params:\r\nall_executions, time_executions, start_time''')
def uses_edit(CurrentUse):
    parser_p = CurrentUse.parser_p
    event_p = CurrentUse.event_p

    alowed_config_params = ['all_executions', 'time_executions', 'start_time']

    params = CurrentUse.text.split(' ')
    if len(params) < 5:
        return "Wrong params count\n" + str(len(params))
    c_action = parser_p.action
    c_howtoget = parser_p.howtoget.split('=')
    c_names = parser_p.names
    try:
        c_config = json.loads(parser_p.configs[0])
    except BaseException:
        # print(sys.exc_info())
        c_config = {}
        for c in parser_p.configs:
            cc = c.split('=')
            try:
                c_config[cc[0]] = int(cc[1])
            except BaseException:

                return "Wrong params string\n" + c
    if c_howtoget[0] == 'fwd':
        if event_p['fwd_messages']:
            uid = event_p['fwd_messages'][0]['from_id']
            c_howtoget = ['vk_id', uid]
        else:
            return "No forwarded messages"

    try:
        obj, is_new = User.objects.get_or_create(**{c_howtoget[0]: c_howtoget[1]})
    except BaseException:
        return "User <" + '='.join(c_howtoget) + "> doesn't exist"

    cur_uses = json.loads(obj.executions)

    for conf_param in c_config:
        if conf_param not in alowed_config_params:
            return 'Wrong param <' + conf_param + '>'

    if c_action == 'jsetall':
        cur_uses = c_config
        c_names = []
    elif c_action == 'setall':
        cur_uses = {}
        c_action = 'add'

    for name in c_names:
        if c_action == 'add':
            if name in cur_uses:
                return "<" + name + "> already exists!"
            cur_uses[name] = c_config
        elif c_action == 'del':
            if name not in cur_uses:
                return "<" + name + ">  not found!"
            cur_uses.pop(name)
        elif c_action == 'upd':
            if name not in cur_uses:
                return "<" + name + "> not found!"
            cur_uses[name].update(c_config)
        elif c_action == 'set':
            if name not in cur_uses:
                return "<" + name + "> not found!"
            cur_uses[name] = c_config

    cur_uses = json.dumps(cur_uses, ensure_ascii=False)
    obj.executions = cur_uses
    obj.save()
    return {'message': "Success!"}


parser = uses_edit.parser
parser.add_argument('action', choices=['jsetall', 'setall', 'add', 'del', 'upd', 'set'])
parser.add_argument('howtoget', help='e.g. vk_id=1')
parser.add_argument('-n', dest='names', metavar='NAME', nargs='*', default=[])
parser.add_argument('-p', dest='configs', help='or json string(WITHOUT SPACES!)', metavar='PARAM=DATA', nargs='*',
                    default={})


@Command('uses.s', hidden=True,
         block='admin_tools',
         description='Shows uses')
def uses_show(CurrentUse):
    parser_p = CurrentUse.parser_p
    event_p = CurrentUse.event_p

    c_howtoget = parser_p.howtoget.split('=')

    if c_howtoget[0] == 'fwd':
        if event_p['fwd_messages']:
            uid = event_p['fwd_messages'][0]['from_id']
            c_howtoget = ['vk_id', uid]
        else:
            return "No forwarded messages"

    try:
        cur_user = User.objects.get(**{c_howtoget[0]: c_howtoget[1]})
    except BaseException:
        return "User <" + '='.join(c_howtoget) + "> doesn't exist"

    cur_user_uses = json.loads(cur_user.executions)
    if parser_p.cmd:
        if parser_p.cmd not in cur_user_uses:
            return 'No uses'
        to_resp = cur_user_uses[parser_p.cmd]
    else:
        to_resp = cur_user_uses
    formatted_json = json.dumps(to_resp, indent='____', ensure_ascii=False)
    return formatted_json


parser = uses_show.parser
parser.add_argument('howtoget', help='e.g. vk_id=1')
parser.add_argument('-c', dest='cmd', help='command', default=False)


@Command('uses', block='defaults', description='Shows current user uses')
def uses_show_my(CurrentUse):
    if CurrentUse.messenger.name == 'VK':
        indent = '&#12288;&#12288;'
    else:
        indent = '  '
    parser_p = CurrentUse.parser_p
    event_p = CurrentUse.event_p

    cur_user = CurrentUse.user
    cur_user_uses = json.loads(cur_user.executions)
    if parser_p.cmd:
        if parser_p.cmd not in cur_user_uses:
            return 'No uses'
        to_resp = cur_user_uses[parser_p.cmd]
    else:
        to_resp = cur_user_uses
    formatted_json = json.dumps(to_resp, indent=indent, ensure_ascii=False)
    return formatted_json


parser = uses_show_my.parser
parser.add_argument('-c', dest='cmd', help='command', default=False)
