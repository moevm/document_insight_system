import json

import pandas as pd

from flask import Blueprint, abort, Response

from app.routes.utils import get_stats, check_export_access

get_csv = Blueprint('get_csv', __name__, template_folder='templates', static_folder='static')


@get_csv.route("/")
def get_csv_main():
    from io import StringIO
    if not check_export_access():
        abort(403)
    response = get_stats()
    df = pd.read_json(StringIO(json.dumps(response)))
    return Response(
        df.to_csv(sep=',', encoding='utf-8', decimal=','),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment"}
    )