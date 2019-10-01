import importlib

from arhisite.settings import BOT_CONFIGURATION

CMD_PREFIX = '/'
BOT_NAME = 'Bot'
BOT_NAME_RUS = 'Бот'

ALLOWED_CMDS = None
ALLOWED_BLOCKS = None
ENABLED_MODULES = ['default']

PASSWD_SALT = ''

JWT_SECRET = ''
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 60 * 60

VK_CALLBACK_SECRET = None
VK_GROUP_TOKEN = None
VK_GROUP_ID = None
VK_CALLBACK_CONFIRM_CODE = None
VK_ENABLE_CONNECTED_GROUPS = False
VK_ALLOW_CONNECT_GROUPS = False
VK_BOT_PARAMS = {
    'startup': 1,
    'forward_first_id': 0
}

TG_BOT_TOKEN = None
TG_BOT_ID = None
TG_BOT_USERNAME = None
TG_PROXY = None
TG_WEBHOOK_SECRET = None
TG_BOT_PARAMS = {}

ANSWER_UNKNOWN_CMD = True
FORWARD = True

LOGGING = True
ERRORS_LOGGING = True

MSG_SEND_ATTEMPTS = 1
MSG_EDIT_ATTEMPTS = 1

IGNORE_OLD = 15

MODULES_SOURCES = ['bot_handler/modules']

MESSENGERS = []

new_variables = importlib.import_module('{}.CONFIG'.format(BOT_CONFIGURATION)).__dict__
globals().update(new_variables)  # todo ???
