import os

from arhisite.settings import BOT_CONFIGURATION

CONFIGURATION_DIR = os.path.dirname(__file__)

BOT_NAME = 'ExampleBot'
BOT_NAME_RUS = 'Ихихи'

ENABLED_MODULES = [
    'default',
    'burger_king',
    'fullshit',
    'joy',
    'raid',
    'testing',
    'tools',
    'vk_antikick',
    'request_uses'
]

PASSWD_SALT = 'KJVnrgugihniurg'

JWT_SECRET = 'VJGEnkdnjUIGHbnrieugj895utrgh'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 60 * 60

VK_CALLBACK_SECRET = 'kevvircarbitAwWypwafwacyifjrituy'
VK_GROUP_TOKEN = '83beab8c95d0d4d22ec83beab8c95d0d4d22e83beab8c95d0d4d22ec67ee9cba50cd4d22ec67ee9cba50c'
VK_GROUP_ID = 173027900
VK_CALLBACK_CONFIRM_CODE = 'a161397c'
VK_ENABLE_CONNECTED_GROUPS = False
VK_ALLOW_CONNECT_GROUPS = False
VK_BOT_PARAMS = {
    'startup': 1,
    'forward_first_id': 0
}

TG_BOT_TOKEN = '782738445:AAHlAAHlspAAHAAHlspcNAHlspcN-m7g-mQ'
TG_BOT_ID = 782738445
TG_PROXY = {'https': 'socks5://95.110.228.190:8975'}
TG_WEBHOOK_SECRET = 'jtttourhtttourhgurhgbkiptttourhg'
TG_BOT_PARAMS = {}

ANSWER_UNKNOWN_CMD = 1
FORWARD = 1

LOGGING = 1
ERRORS_LOGGING = 1

MSG_SEND_ATTEMPTS = 1
MSG_EDIT_ATTEMPTS = 1

IGNORE_OLD = 15

MODULES_SOURCES = [
    'bot_handler/modules',
    os.path.join(BOT_CONFIGURATION, 'modules')
]
