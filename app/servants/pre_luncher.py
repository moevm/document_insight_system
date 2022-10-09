import hashlib
import logging

from pymongo.errors import ConnectionFailure

from db.db_methods import add_user, get_user, get_client, edit_user, save_criteria_pack
from main.check_packs.pack_config import BASE_PACKS
from server import ALLOWED_EXTENSIONS

logger = logging.getLogger('root_logger')


def get_hash(password): return hashlib.md5(password.encode()).hexdigest()


def update_base_check_pack():
    for pack in BASE_PACKS.values():
        save_criteria_pack(pack.to_json())


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

    user.file_type = 'report'
    user.criteria = BASE_PACKS[user.file_type].name
    user.formats = list(ALLOWED_EXTENSIONS.get(user.file_type))
    user.two_files = True
    edit_user(user)

    logger.info(f"Создан администратор по умолчанию: логин: {user.username}, пароль уточняйте у разработчика")

    update_base_check_pack()

    return True
