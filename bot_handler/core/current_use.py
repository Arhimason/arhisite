import collections
import datetime
import json
import re
import time

import telebot

from bot_handler import CONFIG
from bot_handler.core.command import load_commands
from bot_handler.models import Group, UsageLog
from bot_handler.utils import Tools
from bot_handler.utils.argument_parser import WrongArguments
from bot_handler.utils.storage import StorageC
from lib.Tools import get_exc_info


cmds_list = load_commands()


def dict_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = dict_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


class CurrentUse:
    cmds_list = cmds_list
    start_time = time.time()

    def __init__(self, messenger):
        self._traceback = None
        self._comments = {}
        self._logging = CONFIG.LOGGING
        self._responses = []
        self._errors_list = []

        self.event_type = None
        self.peer_id = None
        self.from_id = None
        self.msg_id = None
        self.text = None
        self.date = time.time()

        self.parser_p = None
        self.event_p = None
        self.payload = None

        self.is_action = False
        self.is_pushed = False
        self.in_conversation = False

        self.messenger = messenger
        self.command = None
        self.user = None
        self.usage_log = None

        self.uses_cnt = 1
        self.bot_params = {}
        self.user_result_perms = {}

        # defaults here?
        self.tg_bot_token = None
        self.vk_group = None
        self.ws = None

    def parse_event(self, event):
        cur_object = event['object']
        self.event_p = cur_object
        self.event_type = event['type']
        self.from_id = cur_object['user_id'] if self.event_type in ["message_allow", "message_deny"] else cur_object[
            'from_id']

        self.user, is_new = self.messenger.get_user(self)

        if self.event_type in ["message_reply", "message_new", "message_edit"]:
            self.msg_id = cur_object['id']
            self.peer_id = cur_object['peer_id']
            self.text = cur_object['text']

            self.in_conversation = (self.from_id != self.peer_id)
            self.is_pushed, self.text = self.messenger.check_mentioned(self, self.text)
        else:
            self.peer_id = self.from_id

        if 'payload' in cur_object:
            self.payload = json.loads(cur_object['payload'])
            if 'cmd_str' in self.payload:
                self.text = self.payload['cmd_str']

        self.command = self._get_command()
        if self.command is None:
            response = 'Unknown command'
            if (not CONFIG.ANSWER_UNKNOWN_CMD) or self.in_conversation or self.is_action:
                response = None
            return 0, response

        self._logging = CONFIG.LOGGING and not self.command.disable_log
        if self._logging:
            self.usage_log = UsageLog.objects.create(bot_id=self.messenger.get_bot_id(self),
                                                     user=self.user, peer_id=self.peer_id,
                                                     messenger=self.messenger.name, cmd=self.command.name,
                                                     request=json.dumps(self.event_p, ensure_ascii=False),
                                                     traceback=self._traceback)

        if not self.command.disable_parser:
            success, resp = self._parse_args()
            if not success:
                return 0, resp

        self.uses_cnt = self.command.cnt_func(self.parser_p)

        status, resp = self._handle_permissions()
        if not status:
            return 0, resp

        if self.command.supported_messengers and (self.messenger not in self.command.supported_messengers):
            return 0, 'This command is not supported in this messenger.'

        return 1, None

    def _get_command(self):
        if self.text:
            cmd = re.match(CONFIG.CMD_PREFIX + '(\S+) ?(.*)', self.text, re.DOTALL)
        else:
            cmd = False

        if self.event_type == 'message_new':
            self.date = self.event_p['date']
            if 'action' in self.event_p:
                action_type = self.event_p['action']['type']
                cmd = [0, action_type, self.text]
                self.is_action = True
        else:
            action_type = self.event_type
            cmd = [0, action_type, self.text]
            self.is_action = True

        if not cmd:
            cmd = [0, 'usual_message', self.text]

        cmd_name = cmd[1]
        self.text = cmd[2]

        peer = f'{self.messenger.name}{self.peer_id}'
        user = f'{self.messenger.name}{self.from_id}'
        # user = str(self.user.id)

        if (user in cmds_list['_replace_user_']) and (cmd_name in cmds_list['_replace_user_'][user]):
            return cmds_list['_replace_user_'][user][cmd_name]

        if (peer in cmds_list['_replace_peer_']) and (cmd_name in cmds_list['_replace_peer_'][peer]):
            return cmds_list['_replace_peer_'][peer][cmd_name]

        if cmd_name in cmds_list['main']:
            return cmds_list['main'][cmd_name]

    def _handle_permissions(self):
        cur_user_perms = json.loads(self.user.permissions)
        cur_executions = json.loads(self.user.executions)
        result_perms = {}

        groups_data_raw = Group.objects.filter(name__in=cur_user_perms['groups']).values('permissions', 'name')
        groups_data = {g['name']: json.loads(g['permissions']) for g in groups_data_raw}
        for name in cur_user_perms['groups']:
            result_perms = dict_update(result_perms, groups_data[name])

        result_perms = dict_update(result_perms, cur_user_perms)
        self.user_result_perms = result_perms

        if self.in_conversation:
            peer = f'{self.messenger.name}{self.peer_id}'
        else:
            peer = 'im'

        response = None

        cur_block = self.command.block

        if self.is_action:
            if cur_block == '_ACTIONS_':
                return 1, None
            else:
                return 0, None
        else:
            if cur_block == '_ACTIONS_':
                return 0, "Users can't use action commands"

        if self.user.is_admin:
            return 1, None

        if self.command.name in result_perms['cmds']:
            cmd_perm_info = result_perms['cmds'][self.command.name]
            if ('deny' in cmd_perm_info) and cmd_perm_info['deny']:
                return 0, "You don't have permission to use this command"

            if ('where' in cmd_perm_info) and (peer not in cmd_perm_info['where'].split(',')):
                return 0, "You don't have permission to use this command here"

            if 'time_limit' in cmd_perm_info:
                if self.command.name not in cur_executions:
                    cur_executions[self.command.name] = {'time_executions': 0, 'start_time': time.time()}
                elif 'time_executions' not in cur_executions[self.command.name]:
                    cur_executions[self.command.name].update({'time_executions': 0, 'start_time': time.time()})

                if time.time() > (cur_executions[self.command.name]['start_time'] + cmd_perm_info['timeout']):
                    cur_executions[self.command.name]['time_executions'] = 0
                    cur_executions[self.command.name]['start_time'] = time.time()

                cmd_executions_info = cur_executions[self.command.name]

                if (cmd_perm_info['time_limit'] - cmd_executions_info['time_executions']) < self.uses_cnt:
                    response = "Too many uses(" + str(cmd_perm_info['time_limit']) + ' in ' + str(
                        datetime.timedelta(seconds=cmd_perm_info['timeout'])) + " allowed)"
                    return 0, response

                cur_executions[self.command.name]['time_executions'] += self.uses_cnt
                self.user.executions = json.dumps(cur_executions, ensure_ascii=False)
                self.user.save(update_fields=['executions'])

            if 'all_limit' in cmd_perm_info:
                if self.command.name not in cur_executions:
                    cur_executions[self.command.name] = {'all_executions': 0}
                elif 'all_executions' not in cur_executions[self.command.name]:
                    cur_executions[self.command.name].update({'all_executions': 0})
                cmd_executions_info = cur_executions[self.command.name]

                if (cmd_perm_info['all_limit'] - cmd_executions_info['all_executions']) < self.uses_cnt:
                    response = "Too many uses for you account!"
                    return 0, response

                cur_executions[self.command.name]['all_executions'] += self.uses_cnt
                self.user.executions = json.dumps(cur_executions, ensure_ascii=False)
                self.user.save(update_fields=['executions'])

        elif cur_block in result_perms['blocks']:
            block_perm_info = result_perms['blocks'][cur_block]
            if ('deny' in block_perm_info) and block_perm_info['deny']:
                return 0, "You don't have permission to use this command"

            if ('where' in block_perm_info) and (peer not in block_perm_info['where'].split(',')):
                return 0, "You don't have permission to use this command here"

        else:
            if self.command.allow_group_owner and self.vk_group and \
                    self.vk_group.owner == self.user:
                return 1, response

            if not self.command.allow_default:
                return 0, "You don't have permission to use this command"

        return 1, response

    def _parse_args(self):
        if self.text:
            args = re.split(' +', self.text)
        else:
            args = []

        try:
            parser_p = self.command.parser.parse_args(args)
        except WrongArguments as exc:
            return 0, exc
        except:
            return 0, 'Something went wrong while arguments parsing'

        self.parser_p = parser_p
        return 1, None

    def add_comment(self, name, text, update_now=False):
        if not self._logging:
            return 0

        if type(text) == bytes:
            text = text.decode()
        self._comments[name] = text
        if update_now:
            self.usage_log.comment = json.dumps(self._comments, ensure_ascii=False)
            self.usage_log.save(update_fields=['comment'])

    def finish(self):
        if not self._logging:
            return 0

        all_resps = []
        upd_fields = ['response']

        for message in self._responses:
            if message:
                all_resps.append(message.history)
            else:
                all_resps.append([])

        if self._comments:
            self.usage_log.comment = json.dumps(self._comments, ensure_ascii=False)
            upd_fields.append('comment')

        if self._traceback:
            self.usage_log.traceback = self._traceback
            upd_fields.append('traceback')

        self.usage_log.response = json.dumps(all_resps, ensure_ascii=False)
        self.usage_log.save(update_fields=upd_fields)

    def error_log_add(self, action, request=None, additional=None):
        if not self._logging:
            return 0
        Tools.error_log_add(messenger=self.messenger.name, action=action, request=request, additional=additional,
                            usage_log=self.usage_log)

    def storage(self, use_cur='upc', name=None, user=None, peer=None, cmd=None, load=True):
        if 'u' in use_cur:
            if user:
                raise StorageWrongArguments('<u> and <user> passed')
            user = self.user.id
        if 'p' in use_cur:
            if peer:
                raise StorageWrongArguments('<p> and <peer> passed')
            peer = self.messenger.name + str(self.peer_id)
        if 'c' in use_cur:
            if cmd:
                raise StorageWrongArguments('<c> and <cmd> passed')
            cmd = self.command.name

        return StorageC(name, user, peer, cmd, load)

    def answer_callback_query(self, text):
        if self.messenger.name != 'TG':
            return 0
        text = str(text)
        try:
            resp = telebot.apihelper.answer_callback_query(CONFIG.TG_BOT_TOKEN, self.msg_id, text)
            return 1
        except:
            self.error_log_add('Answering', request=text, additional=get_exc_info())
            return 0

    def send_msg(self, data, **kwargs):
        if data is None:
            return None

        if type(data) != dict:
            data = {'message': str(data)}

        message = self.messenger.send_msg(self, data, **kwargs)

        if self._logging:
            self._responses.append(message)

        return message

        # cur_msg = TGMessage(data, self.peer_id, error_log_add=self.error_log_add, **kwargs)

    def send_keyboard(self, keyboard):
        return self.messenger.send_keyboard(keyboard)

    def cancel_use(self, cnt=None):
        cancel_cnt = self.uses_cnt
        if cnt is not None:
            cancel_cnt = cnt
        self.user.refresh_from_db(fields=['executions'])
        cur_executions = json.loads(self.user.executions)
        if self.command.name not in cur_executions:
            return 1

        curcmd_executions = cur_executions[self.command.name]

        if 'all_executions' in curcmd_executions:
            curcmd_executions['all_executions'] -= cancel_cnt

        if 'time_executions' in curcmd_executions:
            curcmd_executions['time_executions'] -= cancel_cnt

        self.user.executions = json.dumps(cur_executions, ensure_ascii=False)
        self.user.save(update_fields=['executions'])
        return 1


class StorageWrongArguments(Exception):
    def __init__(self, text):
        StorageWrongArguments.txt = text
