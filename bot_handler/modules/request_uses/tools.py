from bot_handler.core.command import Command


@Command('моикарты', block='bk', description='СпИсОк ПрИвЯзАнНыХ КаРт', hidden=True, allow_default=True)
def my_cards(CurrentUse):
    if CurrentUse.in_conversation:
        return 'Нельзя юзать в беседах'
    resp = ''
    u_storage = CurrentUse.storage('u', name='sberb_user')
    if 'cards' not in u_storage:
        return 'Нет прикрепленных карт'
    cards = u_storage['cards']

    for card in cards:
        resp += card['number'] + '\n'
    if not resp:
        return 'Нет прикрепленных карт'
    return resp
