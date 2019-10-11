import time

from bot_handler import CONFIG


def remove_keys(dct, keys):
    dct = dct.copy()
    for key in keys:
        dct.pop(key)
    return dct


def web_to_vk(_, event):
    obj = event
    result = {
        "type": "message_new",
        "object": {
            "date": obj['date'],
            "from_id": obj['user_id'],
            "id": obj['uuid'],
            "out": 0,
            "peer_id": obj['user_id'],
            "text": obj['text'],
            "conversation_message_id": 0,
            "fwd_messages": [],
            "important": False,
            "random_id": 0,
            "attachments": [],
            "is_hidden": False
        },
        "group_id": 0,
    }

    return result


def tg_to_vk(_, event):
    if 'message' in event:
        obj = event['message']
        typee = 'message_new'
    elif 'edited_message' in event:
        obj = event['edited_message']
        typee = 'message_edit'
    elif 'callback_query' in event:
        obj = event['callback_query']['message'].copy()
        obj['from'] = event['callback_query']['from']
        obj['message_id'] = event['callback_query']['id']
        obj['date'] = round(time.time())
        obj['text'] = ''
        typee = 'message_new'
    else:
        raise EventConvertError()

    if 'text' not in obj:
        obj['text'] = ''

    result = {
        "type": typee,
        "object": {
            "date": obj['date'],
            "from_id": obj['from']['id'],
            "id": obj['message_id'],
            "out": 0,
            "peer_id": obj['chat']['id'],
            "text": obj['text'],
            "conversation_message_id": 0,
            "fwd_messages": [],
            "important": False,
            "random_id": 0,
            "attachments": [],
            "is_hidden": False
        },
        "group_id": CONFIG.TG_BOT_ID,
    }

    if 'forward_from' in obj:
        result['object']['from_id'] = event['message']['forward_from']['id']
        result['object']['date'] = event['message']['forward_date']

        fwd_msg = remove_keys(result['object'],
                              ['id', 'out', 'peer_id', 'conversation_message_id', 'important', 'random_id',
                               'is_hidden'])
        fwd_msg['fwd_messages'] = []
        result['object']['fwd_messages'].append(fwd_msg)

        result['object']['from_id'] = obj['from']['id']
        result['object']['date'] = event['message']['date']
        result['object']['text'] = ''

    if 'callback_query' in event:
        result['object']['payload'] = event['callback_query']['data']
        result['object']['parent_id'] = event['callback_query']['message']['message_id']

    return result


class EventConvertError(Exception):
    pass
