from bot_handler.core.command import Command

welcome_message = '''Добро пожаловать в чат!
Всю полезную информацию читать в закреплённом сообщении.
Незнание правил не освобождает от ответственности!'''


# ---------BotFunctions---------


@Command('chat_invite_user_by_link', block='_ACTIONS_', disable_parser=True)
def chat_invite_user_by_link(CurrentUse):
    return welcome_message


@Command('chat_invite_user', block='_ACTIONS_', disable_parser=True)
def chat_invite_user(CurrentUse):
    return welcome_message
