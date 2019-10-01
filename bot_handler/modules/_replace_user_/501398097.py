import json
import random

from bot_handler.core.command import Command


@Command('хавка', block='bk',
         description='Показывает сскока осталось юзов бк',
         hidden=True, allow_default=True)
def check_balance(CurrentUse):
    cmdnames = ['ебалы', 'фрифри', 'бутер']
    resptext = 'Осталось:\n'
    user = CurrentUse.user
    perms = json.loads(user.permissions)
    execs = json.loads(user.executions)

    d = 0
    for cmdname in cmdnames:
        try:
            limit = perms['cmds'][cmdname]['all_limit']
        except:
            limit = -1
            continue
        d = 1
        try:
            usednow = execs[cmdname]['all_executions']
        except:
            usednow = 0
        current = limit - usednow
        if cmdname == 'фрифри':
            current = random.randint(4, 7)

        resptext += '{}: {}\n'.format(cmdname, current)
    if not d:
        return 'Вам бан'

    return resptext


@Command('havka', block='bk',
         description='Показывает сскока осталось юзов бк',
         hidden=True, allow_default=True)
def check_balance(CurrentUse):
    cmdnames = ['ебалы', 'фрифри', 'бутер']
    resptext = 'Осталось:\n'
    user = CurrentUse.user
    perms = json.loads(user.permissions)
    execs = json.loads(user.executions)

    d = 0
    for cmdname in cmdnames:

        try:
            limit = perms['cmds'][cmdname]['all_limit']
        except:
            limit = -1
            continue

        d = 1
        try:
            usednow = execs[cmdname]['all_executions']
        except:
            usednow = 0

        current = limit - usednow

        resptext += '{}: {}\n'.format(cmdname, current)
    if not d:
        return 'Вам бан'

    return resptext
