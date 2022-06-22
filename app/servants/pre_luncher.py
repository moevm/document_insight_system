import hashlib
import logging

from pymongo.errors import ConnectionFailure

from db.db_methods import add_user, get_user, get_client, edit_user

logger = logging.getLogger('root_logger')

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

    logger.info(f"Создан администратор по умолчанию: логин: {user.username}, пароль уточняйте у разработчика")

    return True
