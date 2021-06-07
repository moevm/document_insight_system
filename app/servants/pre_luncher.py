import hashlib
from pymongo.errors import ConnectionFailure

from app.bd_helper.bd_helper import add_user, get_user, get_client, edit_user
from logging import getLogger
logger = getLogger('root')

def get_hash(password): return hashlib.md5(password.encode()).hexdigest()


def init(app, debug):
    try:
        get_client().admin.command('ismaster')
        logger.info("MongoDB работает!")
    except ConnectionFailure:
        logger.error("MongoDB не доступна!")
        return False

    cred_id = "admin"
    cred_pass = app.config['ADMIN_PASSWORD']
    user = get_user(cred_id)

    if user is None:
        user = add_user(cred_id, get_hash(cred_pass))
        user.name = cred_id
        user.is_admin = True
        edit_user(user)

    logger.info("Создан администратор по умолчанию: { логин: " + user.username + ", пароль уточняйте у разработчика }")

    return True
