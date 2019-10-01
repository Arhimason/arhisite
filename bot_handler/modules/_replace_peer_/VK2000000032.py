import vk_api

from bot_handler.core.command import Command
from global_config import VK_MY_TOKEN

welcome_message = '''Хай кст, чекай полностью закреп или бан(если ты картон, то тоже бан)'''


@Command('банкартону', block='rjaki',
         description='Ban kartonu',
         disable_parser=True)
def karton_ban(CurrentUse):
    payload = {
        'member_id': 201061341,
        'chat_id': CurrentUse.peer_id - 2000000000
    }

    resp = CurrentUse.vk_group.api.method('messages.removeChatUser', payload)

    # return resp


@Command('вернутькартона', block='rjaki',
         description='Vernut kartona',
         disable_parser=True)
def karton_return(CurrentUse):
    sess = vk_api.VkApi(token=VK_MY_TOKEN)

    payload = {
        'user_id': 201061341,
        'chat_id': 276,
    }

    resp = sess.method('messages.addChatUser', payload)

    # return resp


@Command('chat_invite_user_by_link', block='_ACTIONS_', disable_parser=True)
def chat_invite_user_by_link(CurrentUse):
    return welcome_message


@Command('chat_invite_user', block='_ACTIONS_', disable_parser=True)
def chat_invite_user(CurrentUse):
    return welcome_message
