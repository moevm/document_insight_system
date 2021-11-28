from flask_login import logout_user, current_user

from app.bd_helper.bd_helper import *

import logging
logger = logging.getLogger('root_logger')

def login(args):
    validation = validate_user(args['username'], args['password_hash'])
    logger.info("Запрошен вход пользователя " + args['username'] + ", " +
          ("вход разрешен" if validation else "во входе отказано"))
    return validation


def signup(args):
    user = add_user(args['username'], args['password_hash'])
    if user is not None:
        user.name = args['name']
        if edit_user(user):
            logger.info("Пользователь " + args['username'] + " зарегистрирован")
            return user
    logger.info("Не удалось зарегистрировать пользователя " + args['username'])
    return None


def logout():
    logger.info(f"Пользователь {current_user.username} вышел")
    logout_user()
    return 'OK'


def signout():
    logger.info("Пользователь " + current_user.username + " удален")
    delete_user(current_user.username)
    logout_user()
    return 'OK'


def edit(json):
    current_user.name = json['name']
    edited = edit_user(current_user)
    logger.info("Пользователь " + current_user.username + ("" if edited else " не") + " изменил имя на " + current_user.name)
    return 'OK' if edited else 'Not OK'


def get_rich(username):
    u = get_user(username)
    for i in range(0, len(u.presentations)):
        u.presentations[i] = get_presentation(u.presentations[i])
        for j in range(0, len(u.presentations[i].checks)):
            u.presentations[i].checks[j] = get_check(u.presentations[i].checks[j])
    return u


def update_criteria(json):
    current_user.criteria = json
    edited = edit_user(current_user)
    logger.info("Пользователь " + current_user.username + ("" if edited else " не") +
          " установил себе критерии проверки: " + str(current_user.criteria))
    return 'OK' if edited else 'Not OK'
