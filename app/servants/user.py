import logging

from flask_login import logout_user, current_user

from db import db_methods

logger = logging.getLogger('root_logger')


def login(args):
    validation = db_methods.validate_user(args['username'], args['password_hash'])
    logger.info("Запрошен вход пользователя " + args['username'] + ", " +
                ("вход разрешен" if validation else "во входе отказано"))
    return validation


def signup(args):
    user = db_methods.add_user(args['username'], args['password_hash'])
    if user is not None:
        user.name = args['name']
        if db_methods.edit_user(user):
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
    db_methods.delete_user(current_user.username)
    logout_user()
    return 'OK'


def edit(json):
    current_user.name = json['name']
    edited = db_methods.edit_user(current_user)
    logger.info(
        "Пользователь " + current_user.username + ("" if edited else " не") + " изменил имя на " + current_user.name)
    return 'OK' if edited else 'Not OK'


def get_rich(username):
    u = db_methods.get_user(username)
    for i in range(0, len(u.presentations)):
        u.presentations[i] = db_methods.get_presentation(u.presentations[i])
        for j in range(0, len(u.presentations[i].checks)):
            u.presentations[i].checks[j] = db_methods.get_check(u.presentations[i].checks[j])
    return u


def update_criteria(json):
    current_user.criteria = json
    edited = db_methods.edit_user(current_user)
    logger.info("Пользователь " + current_user.username + ("" if edited else " не") +
                " установил себе критерии проверки: " + str(current_user.criteria))
    return 'OK' if edited else 'Not OK'
