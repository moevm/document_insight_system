from flask_login import logout_user, current_user

from app.bd_helper.bd_helper import *


def login(args):
    validation = validate_user(args['username'], args['password_hash'])
    print("Запрошен вход пользователя " + args['username'] + ", " +
          ("вход разрешен" if validation else "во входе отказано"))
    return validation


def signup(args):
    user = add_user(args['username'], args['password_hash'])
    if user is not None:
        user.name = args['name']
        if edit_user(user):
            print("Пользователь " + args['username'] + " зарегистрирован")
            return user
    print("Не удалось зарегистрировать пользователя " + args['username'])
    return None


def logout():
    print("Пользователь " + current_user.username + " вышел")
    logout_user()
    return 'OK'


def signout():
    print("Пользователь " + current_user.username + " удален")
    delete_user(current_user.username)
    logout_user()
    return 'OK'


def edit(json):
    current_user.name = json['name']
    edited = edit_user(current_user)
    print("Пользователь " + current_user.username + ("" if edited else " не") + " изменил имя на " + current_user.name)
    return 'OK' if edited else 'Not OK'


def get_rich(username):
    u = get_user(username)
    for i in range(0, len(u.presentations)):
        u.presentations[i] = get_presentation(u.presentations[i])
        for j in range(0, len(u.presentations[i].checks)):
            u.presentations[i].checks[j] = get_check(u.presentations[i].checks[j])
    return u


def update_criteria(json):
    current_user.criteria = Checks(json)
    edited = edit_user(current_user)
    print("Пользователь " + current_user.username + ("" if edited else " не") +
          " установил себе критерии проверки: " + str(current_user.criteria))
    return 'OK' if edited else 'Not OK'
