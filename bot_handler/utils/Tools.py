import json

from bot_handler import CONFIG
from bot_handler.models import ErrorLog


def error_log_add(messenger, action, request=None, additional=None, usage_log=None):
    if CONFIG.ERRORS_LOGGING:
        ErrorLog.objects.create(messenger=messenger, action=action, request=json.dumps(request, ensure_ascii=False),
                                additional=additional, usage_log=usage_log)
