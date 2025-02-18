from flask import Blueprint, request, current_app

from app.db.methods import file as file_methods


capacity = Blueprint('capacity', __name__, template_folder='templates', static_folder='static')


@capacity.route("/", methods=["GET"])
def system_capacity():
    units = {'b': 1, 'mb': 1024 ** 2, 'gb': 1024 ** 3}
    unit = units.get(request.args.get('unit', 'gb').lower(), units['gb'])
    current_size = file_methods.get_storage()
    ratio = current_size / current_app.config['MAX_SYSTEM_STORAGE']
    return {
        'size': current_size / unit,
        'max_size': current_app.config['MAX_SYSTEM_STORAGE'] / unit,
        'ratio': ratio
    }
