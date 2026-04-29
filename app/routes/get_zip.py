import json
import os
import shutil
import tempfile
from io import StringIO
import pandas as pd
from flask import Blueprint, abort, request, Response

from app.routes.utils import get_query, get_stats, check_export_access
from app.db.methods import file as file_methods
from app.db.methods import check as check_methods


get_zip = Blueprint('get_zip', __name__, template_folder='templates', static_folder='static')


@get_zip.route("/")
def get_zip_main():
    if not check_export_access():
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