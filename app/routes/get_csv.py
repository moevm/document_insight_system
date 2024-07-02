import json

import pandas as pd

from flask import Blueprint, abort, Response
from flask_login import login_required, current_user

from app.routes.get_zip import get_stats

get_csv = Blueprint('get_csv', __name__, template_folder='templates', static_folder='static')


@get_csv.route("/")
@login_required
def get_csv_main():
    from io import StringIO
    if not current_user.is_admin:
        abort(403)
    response = get_stats()
    df = pd.read_json(StringIO(json.dumps(response)))
    return Response(
        df.to_csv(sep=',', encoding='utf-8', decimal=','),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment"}
    )