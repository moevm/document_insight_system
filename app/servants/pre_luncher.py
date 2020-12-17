from pymongo.errors import ConnectionFailure

from app.bd_helper.bd_helper import add_user, get_user, get_client, edit_user


def __js_hash(password):
    password_hash = 0
    if len(password) == 0:
        return password_hash
    for char in password:
        password_hash = ((password_hash << 5) - password_hash) + ord(char)
        password_hash = password_hash & password_hash
    return password_hash


def init(debug):
    try:
        get_client().admin.command('ismaster')
        print("MongoDB running!")
    except ConnectionFailure:
        print("MongoDB not available!")
        return False

    if not debug:
        print("Have a nice launch!")
        return True

    cred = "admin"
    user = get_user(cred)
    if user is None:
        user = add_user(cred, __js_hash(cred))
        user.name = cred
        edit_user(user)

    print("Created default user: { login: " + user.username + ", password: " + cred + " }")

    return True
