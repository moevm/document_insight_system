import logging
import re
from datetime import datetime, timedelta

from bson import ObjectId
from flask_login import current_user

logger = logging.getLogger('root_logger')
FILTER_PREFIX = 'filter_'

_SCORE_NUMBER = r"[+-]?\d+(?:[.,]\d+)?"
_SCORE_SINGLE_RE = re.compile(rf"^\s*({_SCORE_NUMBER})\s*$")
_SCORE_RANGE_RE = re.compile(rf"^\s*({_SCORE_NUMBER})\s*-\s*({_SCORE_NUMBER})\s*$")


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


def _end_of_day(value):
    return value.replace(hour=23, minute=59, second=59, microsecond=0)


def _parse_bounds(value, offset):
    parts = [part.strip() for part in (value or '').split(" - ") if part.strip()]
    dates = [_parse_datetime(part) for part in parts]
    if not dates or any(date is None for date in dates):
        return None

    start = dates[0]
    if len(dates) == 1:
        end = _end_of_day(start)
    elif ':' not in parts[1]:
        end = _end_of_day(dates[1])
    else:
        end = dates[1] + timedelta(seconds=59) if dates[1].second == 0 else dates[1]

    return start - offset, end - offset


def _to_score(number):
    return float(number.replace(",", "."))


def _parse_score_bounds(value):
    value = (value or "").strip()
    if not value:
        return None

    range_match = _SCORE_RANGE_RE.match(value)
    if range_match:
        low, high = (_to_score(number) for number in range_match.groups())
        if low > high:
            low, high = high, low
        return {"$gte": low, "$lte": high}

    single_match = _SCORE_SINGLE_RE.match(value)
    if single_match:
        return _to_score(single_match.group(1))

    return None


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

    f_score_raw = filters.get("score", "").strip()
    if f_score_raw:
        score_bounds = _parse_score_bounds(f_score_raw)
        if score_bounds is not None:
            filter_query["score"] = score_bounds
        else:
            logger.warning("Can't apply score filter: %s", f_score_raw)

    # set user filter for current non-admin user
    if not (is_admin or current_user.is_admin):
        filter_query["user"] = current_user.username

    return filter_query
