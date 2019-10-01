from bot_handler.core.command import Command


@Command('addtg', block='defaults', disable_parser=True)
def add_tg(CurrentUse):
    return 'Не робит пока что'
    cur_id = str(CurrentUse.from_id)
    another_id = str(CurrentUse.parser_p.another_id)

    strg = CurrentUse.storage('', cmd='addtg')
