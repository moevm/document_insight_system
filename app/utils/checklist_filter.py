import logging
from datetime import datetime, timedelta

from bson import ObjectId
from flask_login import current_user

logger = logging.getLogger('root_logger')
FILTER_PREFIX = 'filter_'

def _parse_datetime(value):
    value = (value or '').strip()
    if not value:
        return None
    for fmt in ("%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M", "%d.%m.%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None

def _is_date_only(value):
    return value.hour == 0 and value.minute == 0 and value.second == 0

def _parse_bounds(value, offset):
    dates = [_parse_datetime(part) for part in (value or '').split(" - ")]
    if not dates or any(date is None for date in dates):
        return None

    start = dates[0]
    end = dates[1] if len(dates) > 1 else dates[0]
    end += timedelta(hours=23, minutes=59, seconds=59) if _is_date_only(end) else timedelta(seconds=59)
    
    return start - offset, end - offset

def checklist_filter(data, is_admin=False):
    from utils import timezone_offset

    filters = {key[len(FILTER_PREFIX) :]: data[key] for key in data if key.startswith(FILTER_PREFIX)}

    # req filter to mongo query filter conversion
    filter_query = {}

    if f_filename := filters.get("filename"):
        filter_query["filename"] = {"$regex": f_filename, "$options": 'i'}

    if f_user := filters.get("user"):
        filter_query["user"] = {"$regex": f_user, "$options": 'i'}

    if f_criteria := filters.get("criteria"):
        f_criteria = filter(lambda x: x, map(str.strip, f_criteria.split(',')))
        filter_query["criteria"] = {"$regex": '|'.join(f_criteria), "$options": 'i'}

    f_upload_date = filters.get("upload-date", "")
    upload_bounds = _parse_bounds(f_upload_date, timezone_offset)
    if upload_bounds:
        filter_query["_id"] = {
            "$gte": ObjectId.from_datetime(upload_bounds[0]),
            "$lte": ObjectId.from_datetime(upload_bounds[1]),
        }
    elif f_upload_date:
        logger.warning("Can't apply upload-date filter: %s", f_upload_date)

    f_moodle_date = filters.get("moodle-date", "")
    moodle_bounds = _parse_bounds(f_moodle_date, timedelta())
    if moodle_bounds:
        filter_query["lms_passback_time"] = {"$gte": moodle_bounds[0], "$lte": moodle_bounds[1]}
    elif f_moodle_date:
        logger.warning("Can't apply moodle-date filter: %s", f_moodle_date)

    f_score = filters.get("score", "")
    f_score_list = list(filter(lambda val: val, f_score.split("-")))
    try:
        if len(f_score_list) == 1:
            filter_query["score"] = float(f_score_list[0])
        elif len(f_score_list) > 1:
            filter_query["score"] = {"$gte": float(f_score_list[0]), "$lte": float(f_score_list[1])}
    except Exception as e:
        logger.warning("Can't apply score filter")
        logger.warning(repr(e))

    # set user filter for current non-admin user
    if not (is_admin or current_user.is_admin):
        filter_query["user"] = current_user.username

    return filter_query
