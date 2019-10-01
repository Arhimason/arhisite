from bot_handler.core.command import Command

from .utils.GetContact import parse_tags


@Command('gc', block='rjaki',
         description='GetContact tags',
         disable_parser=True)
def gc_tags(CurrentUse):
    phone = CurrentUse.text
    if phone[0] != '+':
        phone = '+' + phone
    if len(phone) != 12:
        return 'ХмХм'
    tags = parse_tags(phone)
    if not tags:
        return 'No data'

    resp = phone + ':\n\n' + '\n'.join(tags)

    return resp
