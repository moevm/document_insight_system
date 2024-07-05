import json
import os
import shutil
import tempfile
from io import StringIO

import pandas as pd

from flask import Blueprint, abort, request, Response
from flask_login import login_required, current_user

from app.db.methods import file as file_methods
from app.db.methods import check as check_methods

from app.utils import checklist_filter, format_check_for_table
from app.server_consts import URL_DOMEN

get_zip = Blueprint('get_zip', __name__, template_folder='templates', static_folder='static')


def get_query(req):
    # query for download csv/zip
    filter_query = checklist_filter(req.args)
    limit = False
    offset = False
    sort = req.args.get("sort", "")
    sort = 'upload-date' if not sort else sort
    order = req.args.get("order", "")
    order = 'desc' if not order else order
    sort = "_id" if sort == "upload-date" else sort
    latest = True if req.args.get("latest") else False
    return dict(filter=filter_query, limit=limit, offset=offset, sort=sort, order=order, latest=latest)


def get_stats():
    rows, count = check_methods.get_checks(**get_query(request))
    return [format_check_for_table(item, set_link=URL_DOMEN) for item in rows]


@get_zip.route("/")
@login_required
def get_zip_main():
    if not current_user.is_admin:
        abort(403)

    original_names = request.args.get('original_names', False) == 'true'

    # create tmp folder
    dirpath = tempfile.TemporaryDirectory()

    # write files
    checks_list, _ = check_methods.get_checks(**get_query(request))
    for check in checks_list:
        db_file = file_methods.find_pdf_by_file_id(check['_id'])
        original_name = check_methods.get_check(check['_id']).filename #get a filename from every check
        if db_file is not None:
            final_name = original_name if (original_name and original_names) else db_file.filename
            # to avoid overwriting files with one name and different content: now we save only last version of pres (from last check)
            if not os.path.exists(f'{dirpath.name}/{final_name}'):
                with open(f"{dirpath.name}/{final_name}", 'wb') as os_file:
                    os_file.write(db_file.read())

    # add csv
    response = get_stats()
    df = pd.read_json(StringIO(json.dumps(response)))
    df.to_csv(f"{dirpath.name}/Статистика.csv")

    # zip
    tmp = tempfile.TemporaryDirectory()
    archive_path = shutil.make_archive(f"{tmp}/archive", 'zip', dirpath.name)
    dirpath.cleanup()

    # send
    with open(archive_path, 'rb') as zip_file:
        return Response(
            zip_file.read(),
            mimetype="application/zip",
            headers={"Content-disposition": "attachment"}
        )