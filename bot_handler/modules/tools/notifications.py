import json

from bot_handler.core.command import Command
from bot_handler.models import User


@Command('nh', block='admin_tools', description='Уведомление держателям команд(ы)')
def notify_holders(CurrentUse):
    commands = CurrentUse.parser_p.commands

    users = User.objects.all()
    users_detailed = {}
    receivers_cnt = 0
    msg_text = ' '.join(CurrentUse.parser_p.text) + '\n[Это сообщение отправлено автоматически]'
    for user in users:
        perms = json.loads(user.permissions)
        execs = json.loads(user.executions)

        users_detailed[user] = {}

        for cmdname in commands:
            try:
                limit = perms['cmds'][cmdname]['all_limit']
            except BaseException:
                limit = -1
                continue

            try:
                usednow = execs[cmdname]['all_executions']
            except BaseException:
                usednow = 0

            cur_cnt = limit - usednow
            if cur_cnt < 0:
                cur_cnt = 0

            if cur_cnt > 0:
                user.notify(msg_text)
                receivers_cnt += 1

            users_detailed[user][cmdname] = cur_cnt

    return 'Отправлено {} человекам'.format(receivers_cnt)


parser = notify_holders.parser
parser.add_argument('-c', '--commands', nargs='*', default=[])
parser.add_argument('-g', '--groups', nargs='*', default=[])
parser.add_argument('text', nargs='*', default=[])
