import hashlib
import json
import random
import time

import telebot

from bot_handler import CONFIG
from lib.Tools import get_exc_info


def default_error_add(*args, **kwargs):
    return 1


class AbstractMessage:
    waiter_postfix = ['.', '..', '...']
    waiter_ind = 0

    def __init__(self, data, error_log_add=default_error_add):
        self.where = None
        self.in_conversation = None
        self.current_data = data.copy()
        self.history = []
        self.error_log_add = error_log_add

        self.msg_id = self._send(data)
        self.is_delivered = True if self.msg_id != -1 else False

    def waiting(self):
        waiter_str = self.waiter_postfix[self.waiter_ind]
        toset = self.current_data.copy()
        toset['message'] += str(waiter_str)
        self.edit(toset, log=False)
        self.waiter_ind += 1
        if self.waiter_ind == len(self.waiter_postfix):
            self.waiter_ind = 0

    def edit(self, data, log=True):
        if type(data) != dict:
            data = {'message': str(data)}

        if log:
            self.current_data = data.copy()
            self.history.append(self.current_data)

        try:
            return self._request_to_edit(data)
        except:
            self.error_log_add('Editing', request=data, additional=get_exc_info())
            return False

    def _send(self, data):
        if type(data) != dict:
            data = {'message': str(data)}

        self.current_data = data.copy()
        self.history.append(self.current_data)

        try:
            msg_id = self._request_to_send(data)
            return msg_id
        except:
            self.error_log_add('Editing', request=data, additional=get_exc_info())
            return -1

    def _request_to_send(self, data):
        return -1

    def _request_to_edit(self, data):
        return False


class TGMessage(AbstractMessage):
    def __init__(self, data, peer_id, *args, **kwargs):
        self.where = 'TG'
        self.peer_id = peer_id
        super(TGMessage, self).__init__(data, *args, **kwargs)

    def _request_to_send(self, data, **kwargs):
        msg_text = data['message']
        resp = telebot.apihelper.send_message(CONFIG.TG_BOT_TOKEN, self.peer_id, msg_text, **kwargs)
        return resp['message_id']

    def _request_to_edit(self, data):
        msg_text = data['message']

        success = telebot.apihelper.edit_message_text(CONFIG.TG_BOT_TOKEN, msg_text, self.peer_id, self.msg_id)
        return success


class VKMessage(AbstractMessage):
    def __init__(self, data, peer_id, vk_api, *args, **kwargs):
        self.where = 'TG'
        self.peer_id = peer_id
        self.vk_api = vk_api
        self.in_conversation = peer_id > 2000000000
        super(VKMessage, self).__init__(data, *args, **kwargs)

    def _request_to_send(self, data):
        data['peer_id'] = self.peer_id
        data['random_id'] = str(random.randint(0, 10000000))

        msg_id = self.vk_api.method('messages.send', data)
        return msg_id

    def _request_to_edit(self, data):
        if self.in_conversation:
            return 0

        data['peer_id'] = self.peer_id
        data['message_id'] = self.msg_id

        return self.vk_api.method('messages.edit', data)


class WEBMessage(AbstractMessage):
    def __init__(self, data, ws, *args, **kwargs):
        self.where = 'WEB'
        self.ws = ws
        super(WEBMessage, self).__init__(data, *args, **kwargs)

    def __gen_msg_id(self, payload):
        serialised = '&'.join('{}={}'.format(a, b) for a, b in payload.items())
        uuid = hashlib.md5(serialised.encode('utf-8')).hexdigest()
        return uuid

    def _request_to_send(self, data):
        data['type'] = 'new_message'
        data['date'] = str(time.time())
        data['text'] = data['message']
        data['message'] = -1
        if 'status' not in data:
            data['status'] = 'ok'

        data['uuid'] = self.__gen_msg_id(data)

        self.ws.send(text_data=json.dumps(data))
        return data['uuid']

    def _request_to_edit(self, data, log=True):
        if 'status' not in data:
            data['status'] = 'ok'

        data['type'] = 'edit_message'
        data['date'] = str(time.time())
        data['text'] = data['message']
        data['uuid'] = self.msg_id
        data['message'] = -1

        self.ws.send(text_data=json.dumps(data))
        return True
