from django.utils.deprecation import MiddlewareMixin

from lib.Notifier import notify
from lib.Tools import get_exc_info


class HandleExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        exc_info = get_exc_info()
        message = exc_info
        notify(message)
        return None
