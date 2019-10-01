import json

import telebot.types

from bot_handler.core.command import Command


@Command('fa.set', block='tools',
         description='Set fast access cmd')
def fast_access_set(CurrentUse):
    if CurrentUse.parser_p.button_index > 10 or CurrentUse.parser_p.button_index < 1:
        return 'You should specify number from 1 to 10'

    button_index = CurrentUse.parser_p.button_index - 1
    command = ' '.join(CurrentUse.parser_p.command)
    label = ' '.join(CurrentUse.parser_p.t)

    if len(command) > 35:
        return 'Command too long(35 chars alowed)'

    if CurrentUse.in_conversation:
        storage = CurrentUse.storage('p', name='fast_access')
    else:
        storage = CurrentUse.storage('u', name='fast_access')

    if 'cmds' not in storage:
        storage['cmds'] = [{}] * 10

    cur_cmd = {'cmd_str': command, 'color': CurrentUse.parser_p.c, 'label': label}

    if not command:
        cur_cmd = {}

    storage['cmds'][button_index] = cur_cmd

    storage.save()

    return 'Success'


parser = fast_access_set.parser
parser.add_argument('button_index', type=int, help='Number from 1 to 10')
parser.add_argument('command', nargs='*', help='e.g: /alive', default=[])
parser.add_argument('-c', choices=['default', 'primary', 'positive', 'negative'], default='default')
parser.add_argument('-t', type=str, default=[], nargs='*')


@Command('fa', block='tools',
         description='Enable\disable fast access')
def fast_access_control(CurrentUse):
    if CurrentUse.in_conversation:
        storage = CurrentUse.storage('p', name='fast_access')
    else:
        storage = CurrentUse.storage('u', name='fast_access')

    if 'cmds' not in storage:
        return 'Fast access is not configured'

    cmds = storage['cmds']

    if CurrentUse.messenger.name == 'VK':
        keybb = {
            "one_time": False,
            "buttons": []
        }

        if CurrentUse.parser_p.d:
            return {"message": "Deactivated", "keyboard": json.dumps(keybb, ensure_ascii=False)}

        for cmd in cmds:
            if not cmd: continue
            labelchik = cmd['label']
            if not labelchik:
                labelchik = cmd['cmd_str']
            btn = {
                "action": {
                    "type": "text",
                    "payload": json.dumps({'cmd_str': cmd['cmd_str']}),
                    "label": labelchik
                },
                "color": cmd['color']
            }

            keybb['buttons'].append([])
            keybb['buttons'][-1].append(btn)

        return {"message": "Activated", "keyboard": json.dumps(keybb, ensure_ascii=False)}
    elif CurrentUse.messenger.name == 'TG':

        if CurrentUse.parser_p.d:
            markup = telebot.types.ReplyKeyboardRemove()
            CurrentUse.send_msg('Activated', reply_markup=markup)
            return None

        markup = telebot.types.ReplyKeyboardMarkup(row_width=10)
        for cmd in cmds:
            if not cmd: continue
            cur_btn = telebot.types.KeyboardButton(cmd['cmd_str'])
            markup.add(cur_btn)
        CurrentUse.send_msg('Activated', reply_markup=markup)


parser = fast_access_control.parser
parser.add_argument('-d', action='store_true', help='disable')


@Command('fa.show', block='tools',
         description='Show current fast access elements')
def fast_access_show(CurrentUse):
    if CurrentUse.in_conversation:
        storage = CurrentUse.storage('p', name='fast_access')
    else:
        storage = CurrentUse.storage('u', name='fast_access')

    if 'cmds' not in storage:
        return 'Fast access is not configured'

    cmds = storage['cmds']

    resp_text = ''

    for i in range(10):
        cur_cmd = cmds[i]
        if not cur_cmd:
            continue

        cur_cmd_text = '{}. {}'.format(i + 1, cur_cmd['cmd_str'])
        if cur_cmd['label']:
            cur_cmd_text += ' (' + cur_cmd['label'] + ')'

        if cur_cmd['color'] != 'default':
            cur_cmd_text += ' [' + cur_cmd['color'] + ']'

        resp_text += cur_cmd_text + '\n'

    return resp_text
