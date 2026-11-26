from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app.db.methods.log import get_logs_cursor
from app.utils.table_query import date_filter, number_filter, page_options, read_filters, text_filter

logs = Blueprint('logs', __name__, template_folder='templates', static_folder='static')


@logs.route("/")
@login_required
def logs_main():
    return render_template("./logs.html", name=current_user.name, navi_upload=True)


@logs.route("/data")
@login_required
def logs_data():
    try:
        filters = read_filters(request.args)
        filter_query = {}
        for field, key in {
            'service-name': 'serviceName',
            'check_id': 'check_id',
            'stage': 'stage',
            'levelname': 'levelname',
            'pathname': 'pathname',
        }.items():
            if value := filters.get(field):
                filter_query[key] = text_filter(value)
        if value := filters.get('lineno'):
            filter_query['lineno'] = number_filter(value, integer=True)
        if value := filters.get('timestamp'):
            filter_query['timestamp'] = date_filter(value)
        if search := request.args.get('search', '').strip():
            filter_query['$or'] = [
                {field: text_filter(search)} for field in ('message', 'check_id', 'serviceName', 'stage')
            ]
        options = page_options(request.args, {'timestamp', 'service-name', 'levelname', 'lineno'}, 'timestamp', 'desc')
    except ValueError as error:
        return jsonify(error=str(error)), 400
    rows, count = get_logs_cursor(filter=filter_query, **options)

    # construct response
    response = {
        "total": count,
        "rows": [
            {
                "timestamp": item["timestamp"].strftime("%d.%m.%Y %H:%M:%S"),
                "check_id": item.get("check_id", None),
                "stage": item.get("stage", None),
                "service-name": item["serviceName"],
                "levelname": item["levelname"],
                "message": item["message"],
                "pathname": item["pathname"],
                "lineno": item["lineno"],
            }
            for item in rows
        ],
    }

    # return json data
    return jsonify(response)
