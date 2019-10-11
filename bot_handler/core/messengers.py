import gc
import json
import re
import time

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from bot_handler import CONFIG
from bot_handler.core.current_use import CurrentUse
from bot_handler.core.messages import VKMessage, TGMessage, WEBMessage, AbstractMessage
from bot_handler.core.converters import web_to_vk, tg_to_vk
from bot_handler.models import ConnectedGroup, User
from bot_handler.utils import jwt_helper
from bot_handler.utils.storage import StorageC

telebot.apihelper.proxy = CONFIG.TG_PROXY


# todo default group
# todo abstract connected prek with bot_params? & save default to db if not exists
def get_group(group_id):
    if CONFIG.VK_GROUP_ID == group_id:
        group = ConnectedGroup(id=group_id,
                               access_token=CONFIG.VK_GROUP_TOKEN,
                               secret=CONFIG.VK_CALLBACK_SECRET,
                               confirm_code=CONFIG.VK_CALLBACK_CONFIRM_CODE)
    elif CONFIG.VK_ENABLE_CONNECTED_GROUPS:
        try:
            group = ConnectedGroup.objects.get(id=group_id)
        except ConnectedGroup.DoesNotExist:
            group = None
    else:
        group = None

    return group


class RunAfterResponse(HttpResponse):
    def __init__(self, content, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        super(RunAfterResponse, self).__init__(content)

    def close(self):
        super(RunAfterResponse, self).close()
        self.func(*self.args, **self.kwargs)


class AbstractMessenger:
    name = 'NAME'
    message = AbstractMessage
    event_converter = None
    answering_mode = 2

    def get_bot_id(self, current_use):
        return 0

    def check_mentioned(self, current_use, text):
        # todo check name and fwd msgs
        # else:
        #     for msg in cur_object['fwd_messages']:
        #         if msg['from_id'] == CONFIG.VK_GROUP_ID:
        #             self.is_pushed = 1
        #             break

        return False, text

    def send_keyboard(self, current_use, keyboard):
        pass
        # todo keyboard abstraction

    def send_msg(self, current_use, data):
        return self.message(data)

    def get_user(self, current_use):
        lower_name = self.name.lower()
        return User.objects.get_or_create(**{f'{lower_name}_id': current_use.from_id})

    # todo handle bad events
    def handle_request(self, *args, **kwargs):
        # event = {}
        # current_use = None
        # self._handle_event(current_use, event)
        pass

    def _handle_event(self, current_use, event):
        if self.event_converter:
            event = self.event_converter(event)

        success, response = current_use.parse_event(event)
        if CONFIG.IGNORE_OLD and (time.time() - current_use.date) > CONFIG.IGNORE_OLD:
            return -2

        if success:
            current_use.command.run(current_use)
        else:
            current_use.send_msg(response)

        current_use.finish()
        gc.collect()


class VKMessenger(AbstractMessenger):
    name = 'VK'
    message = VKMessage

    def get_bot_id(self, current_use):
        return current_use.vk_group.id

    def check_mentioned(self, current_use, text):
        is_pushed = re.search(f'\[club{current_use.vk_group.id}\|([^\]]*)\]', text)
        new_text = re.sub(f'\[club{current_use.vk_group.id}\|([^\]]*)\][ ,]*', '', text)
        return is_pushed, new_text

    @csrf_exempt
    def handle_request(self, request):
        current_use = CurrentUse(self)
        event = json.loads(request.body.decode('utf-8'))

        group_id = event['group_id']
        group = get_group(group_id)
        if group is None:
            return HttpResponse('Hm')

        if event['type'] == 'confirmation':
            return HttpResponse(group.confirm_code)

        if group.secret != event['secret']:
            response = {
                'status': 'error',
                'error': {
                    'code': 403,
                    'text': 'Secret is invalid'
                }
            }
            return JsonResponse(response)

        group.initialize()

        current_use.vk_group = group
        current_use.bot_params = StorageC(obj=group, obj_field='params')

        return RunAfterResponse('ok', self._handle_event,
                                current_use, event)

    def send_msg(self, current_use, data):
        return self.message(data, current_use.peer_id, current_use.vk_group.api,
                            error_log_add=current_use.error_log_add)


class TGMessenger(AbstractMessenger):
    name = 'TG'
    message = TGMessage
    event_converter = tg_to_vk

    def check_mentioned(self, current_use, text):
        is_pushed = re.search(f'@{CONFIG.TG_BOT_USERNAME}$', text)
        new_text = re.sub(f'@{CONFIG.TG_BOT_USERNAME}$', '', text)
        return is_pushed, new_text

    @csrf_exempt
    def handle_request(self, request):
        current_use = CurrentUse(self)
        event = json.loads(request.body.decode('utf-8'))

        if request.GET['secret'] != CONFIG.TG_WEBHOOK_SECRET:
            response = {
                'status': 'error',
                'error': {
                    'code': 403,
                    'text': 'Secret is invalid'
                }
            }
            return JsonResponse(response)

        current_use.tg_bot_token = CONFIG.TG_BOT_TOKEN

        return RunAfterResponse('ok', self._handle_event,
                                current_use, event)

    def send_msg(self, current_use, data):
        return self.message(data, current_use.peer_id, error_log_add=current_use.error_log_add)


# todo как красиво то сделать ммм??
class WEBMessenger(AbstractMessenger):
    name = 'WEB'
    message = WEBMessage
    event_converter = web_to_vk

    def get_user(self, current_use):
        if current_use.user:
            return current_use.user, False
        return User.objects.get_or_create(id=current_use.from_id)

    def handle_request(self, text_data, ws):
        current_use = CurrentUse(self)
        current_use.ws = ws

        event = json.loads(text_data)
        if event['type'] == 'alive':
            return

        try:
            jwt_token = event['token']
        except KeyError:
            ws.send(json.dumps({'status': 'error'}))
            ws.close()
            return

        user, error = jwt_helper.get_user(jwt_token)
        if not user:
            ws.send(json.dumps(error))
            ws.close()
            return

        current_use.user = user

        event['user_id'] = user.id
        self._handle_event(current_use, event)

        # event['ws'] = self

    def send_msg(self, current_use, data):
        return self.message(data, current_use.ws, error_log_add=current_use.error_log_add)
