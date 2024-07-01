import json
from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from app.root_logger import get_root_logger
from datetime import datetime, timedelta
from app.db import db_methods
# from app.server_consts import logger
logs = Blueprint('logs', __name__, template_folder='templates', static_folder='static')
logger = get_root_logger('web')


@logs.route("/")
@login_required
def logs_main():
    return render_template("./logs.html", name=current_user.name, navi_upload=True)


@logs.route("/data")
@login_required
def logs_data():
    filters = request.args.get("filter", "{}")
    try:
        filters = json.loads(filters)
        filters = filters if filters else {}
    except Exception as e:
        logger.warning("Can't parse filters")
        logger.warning(repr(e))
        filters = {}

    # req filter to mongo query filter conversion
    filter_query = {}
    if f_service_name := filters.get("service-name", None):
        filter_query["serviceName"] = {"$regex": f_service_name}

    if f_levelname := filters.get("levelname", None):
        filter_query["levelname"] = {"$regex": f_levelname}

    if f_pathname := filters.get("pathname", None):
        filter_query["pathname"] = {"$regex": f_pathname}

    f_lineno = filters.get("lineno", "")
    f_lineno_list = list(filter(lambda val: val, f_lineno.split("-")))
    try:
        if len(f_lineno_list) == 1:
            filter_query["lineno"] = int(f_lineno_list[0])
        elif len(f_lineno_list) > 1:
            filter_query["lineno"] = {
                "$gte": int(f_lineno_list[0]),
                "$lte": int(f_lineno_list[1])
            }
    except Exception as e:
        logger.warning("Can't apply lineno filter")
        logger.warning(repr(e))

    f_timestamp = filters.get("timestamp", "")
    f_timestamp_list = list(filter(lambda val: val, f_timestamp.split("-")))
    try:
        if len(f_timestamp_list) == 1:
            date = datetime.strptime(f_timestamp_list[0], "%d.%m.%Y")
            filter_query['timestamp'] = {
                "$gte": date,
                "$lte": date + timedelta(hours=23, minutes=59, seconds=59)
            }
        elif len(f_timestamp_list) > 1:
            filter_query['timestamp'] = {
                "$gte": datetime.strptime(f_timestamp_list[0], "%d.%m.%Y"),
                "$lte": datetime.strptime(f_timestamp_list[1], "%d.%m.%Y")
            }
    except Exception as e:
        logger.warning("Can't apply timestamp filter")
        logger.warning(repr(e))

    # parse and validate rest query
    limit = request.args.get("limit", "")
    limit = int(limit) if limit.isnumeric() else 10

    offset = request.args.get("offset", "")
    offset = int(offset) if offset.isnumeric() else 0

    sort = request.args.get("sort", "")
    sort = 'timestamp' if not sort else sort

    order = request.args.get("order", "")
    order = 'desc' if not order else order

    # get data and records count
    rows, count = db_methods.get_logs_cursor(filter=filter_query, limit=limit, offset=offset, sort=sort, order=order)

    # construct response
    response = {
        "total": count,
        "rows": [{
            "timestamp": item["timestamp"].strftime("%d.%m.%Y %H:%M:%S"),
            "service-name": item["serviceName"],
            "levelname": item["levelname"],
            "message": item["message"],
            "pathname": item["pathname"],
            "lineno": item["lineno"]
        } for item in rows]
    }

    # return json data
    return jsonify(response)

