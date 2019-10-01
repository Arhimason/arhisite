from bot_handler.core.command import Command
from vk_antikick import antikick


# ---------BotFunctions---------


@Command('ak', )
def toggle(CurrentUse):
    parser_p = CurrentUse.parser_p
    resptext = ''
    enable = 1
    if parser_p.d:
        enable = 0
    r = antikick.toggle(parser_p.chat_id, enable)
    resptext += 'toggle: {}\n'.format(r)
    if not r:
        return resptext
    running = antikick.status()
    resptext += 'status: {} {}\n'.format(running[0], running[1])
    if running[0]:
        sto = antikick.stop()
        sta = antikick.start()
        resptext += 'stop: {}\nstart: {}\n'.format(sto, sta)

    return resptext


parser = toggle.parser
parser.add_argument('chat_id', type=int)
parser.add_argument('-d', action='store_true', default=False)


@Command('ak.stop', )
def stop(CurrentUse):
    r = antikick.stop()
    return r


@Command('ak.status', )
def status(CurrentUse):
    r = antikick.status()
    return 'sockets: {}\nprocess {}'.format(r[0], r[1])


@Command('ak.chats', )
def chat_list(CurrentUse):
    resptext = ''
    chats = antikick.chat_list()
    for chat in chats:
        if not chat['antikick'] and not CurrentUse.parser_p.a: continue
        resptext += '{} {}\n'.format(chat['id'], chat['antikick'])
    return resptext


parser = chat_list.parser
parser.add_argument('-a', action="store_true")


@Command('ak.start', )
def start(CurrentUse):
    return antikick.start()


@Command('ak.sync', )
def sync_bots(CurrentUse):
    return antikick.update_bots_info()


@Command('ak.add_bot', disable_parser=True)
def add_bot(CurrentUse):
    CurrentUse.text = CurrentUse.text.replace(':', ';')
    CurrentUse.text = CurrentUse.text.replace(' ', ';')
    datas = CurrentUse.text.split(';')
    token = None
    if len(datas) > 2:
        if len(datas[2]) > 30:
            token = datas[2]
    return antikick.add_bot(datas[0], datas[1], token=token)


@Command('ak.restart', )
def restart(CurrentUse):
    sto = antikick.stop()
    sta = antikick.start()
    return 'stop: {}\nstart: {}'.format(sto, sta)
