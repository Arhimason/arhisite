import json
import re
from collections import OrderedDict
from datetime import datetime

from pytz import timezone

from bot_handler.core.command import Command
from bot_handler.utils.storage import StorageC


@Command('warn', hidden=True,
         block='warns', description='Дает предупреждение угум',
         disable_parser=True)
def warn(CurrentUse):
    max_warns = 3
    event_p = CurrentUse.event_p
    params = re.match('(\S+) ?(.*)', CurrentUse.text, re.DOTALL)
    if not params:
        return 'mm??'

    howtofet = params[1]
    if howtofet == 'fwd':
        if event_p['fwd_messages']:
            id = event_p['fwd_messages'][0]['from_id']
        else:
            return 'No forwarded messages'
    else:
        mtch = re.match('\[id([0-9]*)\|([^\]]*)\]', howtofet)
        if mtch:
            id = mtch[1]
        else:
            return 'mm??'

    try:
        decription = params[2]
    except IndexError:
        decription = ''

    now_time = datetime.now(timezone('Europe/Saratov'))
    now_time = now_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    curwarn = {'date': now_time, "decription": decription, 'admin': CurrentUse.from_id}
    storage = CurrentUse.storage('pc', user=id)
    if 'warns' not in storage:
        storage['warns'] = []

    storage['warns'].append(curwarn)
    storage.save()
    resp = 'Готово. Теперь у этого пользователя ' + str(len(storage['warns']))
    if len(storage['warns']) == 1:
        resp += ' предупреждение.'
    else:
        resp += ' предупреждения.'

    kick = 0
    if len(storage['warns']) == (max_warns - 1):
        resp += '\nК слову, оно явлеятся последним. Еще одно и пользователь будет исключен'
    elif len(storage['warns']) >= max_warns:
        resp += '\nПока-пока!'
        kick = 1

    resp += '\n\n P.S: Предупреждения можно попытаться оспорить. Для этого пишите в лс маладому админу беседы)'
    CurrentUse.send_msg(resp)

    if kick:
        payload = {"member_id": id,
                   "chat_id": CurrentUse.peer_id - 2000000000}

        for i in range(3):
            try:
                resp = CurrentUse.vk_group.api.method('messages.removeChatUser', payload)
            except BaseException:
                resp = 0
            if resp: break

    return None


@Command('dewarn', hidden=True,
         block='warns', description='Убирает последнее предупреждение угум',
         disable_parser=True)
def dewarn(CurrentUse):
    max_warns = 3
    event_p = CurrentUse.event_p
    params = re.match('(\S+) ?(.*)', CurrentUse.text, re.DOTALL)
    if not params:
        return 'mm??'

    howtofet = params[1]

    if howtofet == 'fwd':
        if event_p['fwd_messages']:
            id = event_p['fwd_messages'][0]['from_id']
        else:
            return 'No forwarded messages'
    else:
        mtch = re.match('\[id([0-9]*)\|([^\]]*)\]', howtofet)
        if mtch:
            id = mtch[1]
        else:
            return 'mm??'

    storage = CurrentUse.storage('p', user=id, cmd='warn')
    if 'warns' not in storage:
        storage['warns'] = []
        return 'У этого пользователя и так нет прудепреждений, мдауш....'
    if len(storage['warns']) == 0:
        return 'У этого пользователя и так нет прудепреждений, мдауш....'

    storage['warns'].pop()
    storage.save()

    resp = 'Готово. Теперь у этого пользователя ' + str(len(storage['warns']))
    if len(storage['warns']) == 0:
        resp += ' предупреждений'
    elif len(storage['warns']) == 1:
        resp += ' предупреждение.'
    else:
        resp += ' предупреждения.'

    if len(storage['warns']) == (max_warns - 1):
        resp += '\nК слову, оно явлеятся последним. Еще одно и пользователь будет исключен'
    elif len(storage['warns']) >= max_warns:
        resp += '\nОн будет кикнут при получении еще одного варна.'

    return resp


@Command('warns.s', hidden=True,
         block='warns', description='Показует варны юзера',
         disable_parser=True)
def show_warns(CurrentUse):
    event_p = CurrentUse.event_p
    params = re.match('(\S+) ?(.*)', CurrentUse.text, re.DOTALL)
    if not params:
        return 'mm??'

    howtofet = params[1]

    if howtofet == 'fwd':
        if event_p['fwd_messages']:
            id = event_p['fwd_messages'][0]['from_id']
        else:
            return 'No forwarded messages'
    else:
        mtch = re.match('\[id([0-9]*)\|([^\]]*)\]', howtofet)
        if mtch:
            id = mtch[1]
        else:
            return 'mm??'

    storage = CurrentUse.storage('p', user=id, cmd='warn')
    if 'warns' not in storage:
        storage['warns'] = []

    formatted_json = json.dumps(storage['warns'], indent='____', ensure_ascii=False)

    return formatted_json


@Command('заманю', block='zaman',
         description='Returns the link to page of somebody, who probably interested in table games',
         hidden=True, disable_parser=True, allow_default=True)
def zamanit(CurrentUse):
    idsFilePath = 'cmds/ids.txt'
    with open(idsFilePath) as idsFile:
        ids = idsFile.read().split('\n')
    id = ids.pop(0)
    from_id = str(CurrentUse.from_id)
    with open(idsFilePath, 'w') as accountsFile:
        accountsFile.write('\n'.join(ids))

    storage = StorageC(name='zaman')
    if 'ids_received' not in storage:
        storage['ids_received'] = {}

    if from_id not in storage['ids_received']:
        storage['ids_received'][from_id] = []

    storage['ids_received'][from_id].append(id)
    storage.save()
    return 'https://vk.com/id{}\nСсылка на беседу: {}\n'.format(id, 'https://vk.me/join/AJQ1d/0CaQmKzKONEeHMeSu2')


@Command('заманаторы', block='zaman',
         description='Returns the link to page of somebody, who probably interested in table games',
         hidden=True, disable_parser=True, allow_default=True)
def zamanatori(CurrentUse):
    storage = StorageC(name='zaman')

    uinfs = {}

    for uid, user_ids_received in storage['ids_received'].items():
        if uid not in uinfs:
            uinfs[uid] = [0, 0, '']
        uinfs[uid][0] = len(user_ids_received)

    for uid, user_ids_zamaned in storage['zamaned'].items():
        if uid not in uinfs:
            uinfs[uid] = [0, 0, '']
        uinfs[uid][1] = len(user_ids_zamaned)

    resp = ''

    payload = {
        'user_ids': ','.join(uinfs.keys()),
        'fields': ''
    }
    user_datas = CurrentUse.vk_group.api.method('users.get', payload)
    for user_data in user_datas:
        cur_id = str(user_data['id'])
        fname = user_data['first_name']
        lname = user_data['last_name']
        uinfs[cur_id][2] = fname + ' ' + lname

    uinfs = OrderedDict(sorted(uinfs.items(), key=lambda t: t[1][1], reverse=True))
    for uid, data in uinfs.items():
        resp += '----- ' + data[2] + ' -----\n'
        resp += 'Заманено: ' + str(data[1]) + '\n'
        resp += 'Запусков /заманю: ' + str(data[0]) + '\n'
        resp += '----- https://vk.com/id' + uid + ' -----\n\n'
    return resp
