import hashlib
import json
import socket
import sys
import time
import traceback
from queue import Queue
from threading import Thread

import requests
import vk_api


# todo sort tools to sections
def get_exc_info(add_traceback=True):
    response = ''
    exc_info = sys.exc_info()
    response += str(exc_info[0]) + ', ' + str(exc_info[1])

    if add_traceback:
        response += '\n\nTraceback:\n' + ''.join(traceback.format_tb(exc_info[2]))
    return response


class Session(requests.Session):
    def prepare_request(self, request):
        r = super(Session, self).prepare_request(request)
        r.headers = dict(r.headers)
        r.headers.update(self.headers)
        r.headers.update(request.headers)
        return r


class EasyThreading:
    def decorator_maker(self, func):

        def result_func():
            while True:
                payload = self.q.get()
                try:
                    response = func(payload)
                except:
                    print(get_exc_info())
                    response = 0

                self.responses[payload['key']] = response
                self.q.task_done()

        return result_func

    def __init__(self, target, concurrent=50):
        self.target = self.decorator_maker(target)
        self.concurrent = concurrent
        self.q = None
        self.payloads = []
        self.responses = {}

    def add_payload(self, payload):
        if 'key' not in payload:
            payload['key'] = len(self.payloads)

        self.payloads.append(payload)

    def finish(self):
        if len(self.payloads) < self.concurrent:
            self.concurrent = len(self.payloads)

        self.q = Queue(self.concurrent)

        for i in range(self.concurrent):
            t = Thread(target=self.target)
            t.daemon = True
            t.start()

        try:
            for payload in self.payloads:
                self.q.put(payload)
            self.q.join()
        except KeyboardInterrupt:
            raise Exception('ARGH ERR')

        return self.responses


class ExecuteStack:
    def __init__(self, vk_session):
        self.stack = []
        self.responses = []
        self.vk_session = vk_session

    def add(self, method, payload, additional=None):
        cur = (method, payload, additional)
        self.stack.append(cur)
        if len(self.stack) == 25:
            self.execute()

    def execute(self):
        if not self.stack:
            return 0
        code = 'var ret = [];'
        for obj in self.stack:
            code += 'ret = ret + [API.' + obj[0] + '(' + json.dumps(obj[1], ensure_ascii=False) + ')];'
        code += 'return ret;'
        payload = {'code': code}
        resp = self.vk_session.method('execute', payload)

        for r in resp:
            additional = self.stack.pop(0)[2]
            cur = (r, additional)
            self.responses.append(cur)

    def finish(self):
        self.execute()
        return self.responses

    def wipe_responses(self):
        self.responses = []
        return 1


def already_running(process_name, donthold=False):
    already_running._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        already_running._lock_socket.bind('\0' + process_name)
        if donthold:
            already_running._lock_socket.close()
        return 0
    except socket.error:
        return 1


class VkApi2(vk_api.VkApi):
    def __init__(self, secret=None, sid=None, app_id=2274003, app_sec='hHbZxrka2uZ6jB1inYsH', *args, **kwargs):
        self.secret = secret
        self.sid = sid
        self.app_sec = app_sec
        kwargs['app_id'] = app_id
        super(VkApi2, self).__init__(*args, **kwargs)
        if self.sid:
            my_cookie = {
                "version": 0,
                "name": 'remixsid',
                "value": sid,
                "port": None,
                # "port_specified":False,
                "domain": 'vk.com',
                # "domain_specified":False,
                # "domain_initial_dot":False,
                "path": '/',
                # "path_specified":True,
                "secure": False,
                "expires": None,
                "discard": True,
                "comment": None,
                "comment_url": None,
                "rest": {},
                "rfc2109": False
            }

            self.http.cookies.set(**my_cookie)

    def method(self, method, values=None, captcha_sid=None, captcha_key=None,
               raw=False):
        """ Вызов метода API

        :param method: название метода
        :type method: str

        :param values: параметры
        :type values: dict

        :param captcha_sid: id капчи
        :type captcha_key: int or str

        :param captcha_key: ответ капчи
        :type captcha_key: str

        :param raw: при False возвращает `response['response']`
                    при True возвращает `response`
                    (может понадобиться для метода execute для получения
                    execute_errors)
        :type raw: bool
        """

        values = values.copy() if values else {}

        if 'v' not in values:
            values['v'] = self.api_version

        if self.token:
            values['access_token'] = self.token['access_token']

        if captcha_sid and captcha_key:
            values['captcha_sid'] = captcha_sid
            values['captcha_key'] = captcha_key

        if self.secret:
            sig = '&'.join("{!s}={!s}".format(key, val) for (key, val) in values.items())
            sig = '/method/' + method + '?' + sig + self.secret
            sig = sig.encode('utf-8')
            sig = hashlib.md5(sig).hexdigest()
            values['sig'] = sig

        with self.lock:
            # Ограничение 3 запроса в секунду
            delay = self.RPS_DELAY - (time.time() - self.last_request)

            if delay > 0:
                time.sleep(delay)

            response = self.http.post(
                'https://api.vk.com/method/' + method,
                values
            )
            self.last_request = time.time()

        if response.ok:
            response = response.json()
        else:
            error = vk_api.exceptions.ApiHttpError(self, method, values, raw, response)
            response = self.http_handler(error)

            if response is not None:
                return response

            raise error

        if 'error' in response:
            error = vk_api.exceptions.ApiError(self, method, values, raw, response['error'])

            if error.code in self.error_handlers:
                if error.code == vk_api.exceptions.CAPTCHA_ERROR_CODE:
                    error = vk_api.exceptions.Captcha(
                        self,
                        error.error['captcha_sid'],
                        self.method,
                        (method,),
                        {'values': values, 'raw': raw},
                        error.error['captcha_img']
                    )

                response = self.error_handlers[error.code](error)

                if response is not None:
                    return response

            raise error

        return response if raw else response['response']

    def _api_login(self):
        """ Получение токена через Desktop приложение """

        url = 'https://oauth.vk.com/token?grant_type=password&client_id={}&client_secret={}&username={}&password={}'.format(
            self.app_id, self.app_sec, self.login, self.password)

        req = requests.get(url)

        resp = req.json()
        if 'access_token' not in resp:
            print(resp)
            raise Exception('err')

        access_token = resp['access_token']
        user_id = resp['user_id']
        self.token = resp
        self.storage.setdefault(
            'token', {}
        ).setdefault(
            'app' + str(self.app_id), {}
        )['scope_' + str(self.scope)] = resp
        self.storage.save()
        self.logger.info('Got access_token')
