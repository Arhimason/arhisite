from bot_handler.core.command import Command


# ---------BotFunctions---------


# def message_typing_state(CurrentUse):
#     if CurrentUse.in_conversation: return
#     return 'Аккуратнее пиши свои буковки.....'
# cur_command = Command('message_typing_state', message_typing_state,
#                       block='_ACTIONS_', disable_parser=True)
# cur_command.add_to_list()


# def message_edit(CurrentUse):
#     return 'Нах сообщения редачишь мм??'
# cur_command = Command('message_edit', message_edit,
#                       block='_ACTIONS_', disable_parser=True)
# cur_command.add_to_list()


@Command('chat_invite_user_by_link', block='_ACTIONS_', disable_parser=True)
def chat_invite_user_by_link(CurrentUse):
    return None
    return 'Привет!'


@Command('chat_invite_user', block='_ACTIONS_', disable_parser=True)
def chat_invite_user(CurrentUse):
    return None
    return 'Привет!'
