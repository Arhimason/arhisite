from bot_handler.core.command import Command

welcome_message = '''Гуччимейн вошел'''


# ---------BotFunctions---------


@Command('chat_invite_user_by_link', block='_ACTIONS_', disable_parser=True)
def chat_invite_user_by_link(CurrentUse):
    return welcome_message


@Command('chat_invite_user', block='_ACTIONS_', disable_parser=True)
def chat_invite_user(CurrentUse):
    invited_id = CurrentUse.event_p['action']['member_id']
    if invited_id != CurrentUse.from_id:
        return None

    return welcome_message


@Command('chat_kick_user', block='_ACTIONS_', disable_parser=True)
def chat_kick_user(CurrentUse):
    member_id = CurrentUse.event_p['action']['member_id']
    if member_id == CurrentUse.from_id:
        return 'Гуччимейн вышел'
    else:
        return None
    # return random.choice(frzs)
