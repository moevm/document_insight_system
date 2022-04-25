import json
import logging
from datetime import datetime, timedelta

from bson import ObjectId
from flask_login import current_user
from app.utils.time import timezone_offset

logger = logging.getLogger('root_logger')


def checklist_filter(request):
    # transform json filter into dict
    filters = request.args.get("filter", "{}")
    try:
        filters = json.loads(filters)
        filters = filters if filters else {}
    except Exception as e:
        logger.warning("Can't parse filters")
        logger.warning(repr(e))
        filters = {}

    # request filter to mongo query filter conversion
    filter_query = {}
    if f_filename := filters.get("filename", None):
        filter_query["filename"] = { "$regex": f_filename }

    if f_user := filters.get("user", None):
        filter_query["user"] = { "$regex": f_user }

    f_upload_date = filters.get("upload-date", "")
    f_upload_date_list = list(filter(lambda val: val, f_upload_date.split("-")))
    try:
        if len(f_upload_date_list) == 1:
            date = datetime.strptime(f_upload_date_list[0], "%d.%m.%Y") - timezone_offset
            filter_query["_id"] = {
                "$gte": ObjectId.from_datetime(date),
                "$lte": ObjectId.from_datetime(date + timedelta(hours=23, minutes=59, seconds=59))
            }
        elif len(f_upload_date_list) > 1:
            filter_query["_id"] = {
                "$gte": ObjectId.from_datetime(datetime.strptime(f_upload_date_list[0], "%d.%m.%Y") - timezone_offset),
                "$lte": ObjectId.from_datetime(datetime.strptime(f_upload_date_list[1], "%d.%m.%Y") - timezone_offset)
            }
    except Exception as e:
        logger.warning("Can't apply upload-date filter")
        logger.warning(repr(e))

    f_moodle_date = filters.get("moodle-date", "")
    f_moodle_date_list = list(filter(lambda val: val, f_moodle_date.split("-")))
    try:
        if len(f_moodle_date_list) == 1:
            date = datetime.strptime(f_moodle_date_list[0], "%d.%m.%Y")
            filter_query['lms_passback_time'] = {
                "$gte": date,
                "$lte": date + timedelta(hours=23, minutes=59, seconds=59)
            }
        elif len(f_moodle_date_list) > 1:
            filter_query['lms_passback_time'] = {
                "$gte": datetime.strptime(f_moodle_date_list[0], "%d.%m.%Y"),
                "$lte": datetime.strptime(f_moodle_date_list[1], "%d.%m.%Y")
            }
    except Exception as e:
        logger.warning("Can't apply moodle-date filter")
        logger.warning(repr(e))

    f_score = filters.get("score", "")
    f_score_list = list(filter(lambda val: val, f_score.split("-")))
    try:
        if len(f_score_list) == 1:
            filter_query["score"] = float(f_score_list[0])
        elif len(f_score_list) > 1:
            filter_query["score"] = {
                "$gte": float(f_score_list[0]),
                "$lte": float(f_score_list[1])
            }
    except Exception as e:
        logger.warning("Can't apply score filter")
        logger.warning(repr(e))

    # set user filter for current non-admin user
    if not current_user.is_admin:
        filter_query["user"] = current_user.username

    return filter_query
