import jwt

from bot_handler.CONFIG import JWT_SECRET, JWT_ALGORITHM
from bot_handler.models import User


def get_user(jwt_token):
    try:
        payload = jwt.decode(jwt_token, JWT_SECRET,
                             algorithms=[JWT_ALGORITHM])
    except jwt.DecodeError:
        response = {
            'status': 'error',
            'error': {
                'code': 400,
                'text': 'Token is invalid'
            }
        }
        return False, response
    except jwt.ExpiredSignatureError:
        response = {
            'status': 'error',
            'error': {
                'code': 403,
                'text': 'Token is expired'
            }
        }
        return False, response

    try:
        cur_user = User.objects.get(id=payload['user_id'])
    except User.DoesNotExist:
        response = {
            'status': 'error',
            'error': {
                'code': 403,
                'text': 'User has been deleted'
            }
        }
        return False, response

    return cur_user, {}
