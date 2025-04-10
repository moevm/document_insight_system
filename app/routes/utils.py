from flask import request
from flask_login import current_user
import os

from app.db import db_methods
from app.server_consts import URL_DOMEN
from app.utils import checklist_filter, format_check_for_table


def check_access_token(access_token):
    # if request has access_token, and it's equal to ACCESS_TOKEN from env -> accept, esle - check user
    return access_token and (access_token == os.environ.get('ACCESS_TOKEN'))


def check_export_access():
    return check_access_token(request.args.get('access_token', None)) \
           or (current_user.is_authenticated and current_user.is_admin)


def get_query(req):
    # query for download csv/zip (only for admins)
    filter_query = checklist_filter(req.args, is_admin=True)
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
    rows, _ = db_methods.get_checks(**get_query(request))
    return [format_check_for_table(item, set_link=URL_DOMEN) for item in rows]
