import hashlib

from bot_handler import CONFIG
from bot_handler.core.command import Command
from bot_handler.models import User


@Command('setpass', block='defaults', disable_parser=True,
         description='Set current user password to web version')
def set_password(CurrentUse):
    passwd = CurrentUse.text
    if len(passwd) < 5:
        return 'Too short'

    passwd_hash = hashlib.sha256((passwd + CONFIG.PASSWD_SALT).encode()).hexdigest()
    CurrentUse.user.password = passwd_hash
    CurrentUse.user.save(update_fields=['password'])
    return 'Success'


@Command('setlogin', block='defaults', disable_parser=True,
         description='Set current user login to web version')
def set_login(CurrentUse):
    login = CurrentUse.text
    if len(login) < 4:
        return 'Too short'

    exists = User.objects.filter(login=login).exists()
    if exists:
        return 'This login is already in use'

    CurrentUse.user.login = login
    CurrentUse.user.save(update_fields=['login'])
    return 'Success'
