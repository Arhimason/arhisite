import hashlib
import json
from datetime import datetime, timedelta

import jwt
from django.http import JsonResponse
# chat/views.py
from django.shortcuts import render

from bot_handler.CONFIG import PASSWD_SALT, JWT_SECRET, JWT_ALGORITHM, JWT_EXP_DELTA_SECONDS, BOT_NAME
from bot_handler.models import User
from .utils import jwt_helper


# todo load messages from db
def index(request):
    jwt_token = request.COOKIES.get('token')

    user, error = jwt_helper.get_user(jwt_token)

    if not user:
        return render(request, 'index.html', {'logged_in': 0, 'bot_name': BOT_NAME})

    return render(request, 'index.html', {'logged_in': 1, 'form_style': "visibility: hidden; opacity:0;",
                                          'login': user.login, 'bot_name': BOT_NAME})


def auth(request):
    try:
        req_data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        response = {
            'status': 'error',
            'error': {
                'code': 400,
                'text': 'Request is invalid'
            }
        }
        return JsonResponse(response, status=400)

    login = req_data['login']
    password = req_data['password']
    password_hash = hashlib.sha256((password + PASSWD_SALT).encode()).hexdigest()

    try:
        user = User.objects.get(login=login, password=password_hash)
    except User.DoesNotExist:
        response = {
            'status': 'error',
            'error': {
                'code': 403,
                'text': 'Incorrect login/password'
            }
        }
        return JsonResponse(response, status=403)

    exp = datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    payload = {
        'user_id': user.id,
        'exp': exp,
    }

    jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM).decode()

    response = {'status': 'ok'}
    response = JsonResponse(response)
    response.set_cookie(key='token', value=jwt_token, path='/bot_handler', expires=exp)
    return response
