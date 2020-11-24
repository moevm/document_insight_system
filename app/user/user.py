from app.bd_helper.bd_helper import add_user, validate_user, edit_user


def login(args):
    return validate_user(args['username'], args['password_hash'])


def signup(args):
    user = add_user(args['username'], args['password_hash'])
    if user is not None:
        user.name = args['name']
        if edit_user(user):
            return user
    return None
