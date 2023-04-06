from .timezone import timezone_offset
from flask import url_for

def format_check(check):
    grade_passback_time = check['lms_passback_time']
    grade_passback_ts = grade_passback_time.strftime(
        "%H:%M:%S - %b %d %Y") if grade_passback_time else '-'
    return (str(check['_id']), check['user'], check['filename'], check['criteria'],
            (check['_id'].generation_time + timezone_offset).strftime("%H:%M:%S - %b %d %Y"),
            grade_passback_ts, check['score'])


def format_check_for_table(check, set_link=None):
    return {
        "_id": str(check["_id"]),
        "filename": check["filename"],
        "criteria": check.get("criteria", ''),
        "user": check["user"],
        "lms-username": check["user"].rsplit('_', 1)[0],
        "lms-user-id": check["lms_user_id"] if check.get("lms_user_id") else '-',
        "upload-date": (check["_id"].generation_time + timezone_offset).strftime("%d.%m.%Y %H:%M:%S"),
        "moodle-date": check['lms_passback_time'].strftime("%d.%m.%Y %H:%M:%S") if check.get(
            'lms_passback_time') else '-',
        "score": check["score"],
        "link": f"{set_link}{url_for('results',_id=check['_id'])}" if set_link else ''
    }
