from flask import url_for

from .timezone import timezone_offset


def format_check(check):
    grade_passback_time = check['lms_passback_time']
    grade_passback_ts = grade_passback_time.strftime("%H:%M:%S - %b %d %Y") if grade_passback_time else '-'
    return (
        str(check['_id']),
        check['user'],
        check['filename'],
        check['criteria'],
        (check['_id'].generation_time + timezone_offset).strftime("%H:%M:%S - %b %d %Y"),
        grade_passback_ts,
        check['score'],
    )


def format_check_for_table(check, set_link=None, include_status=False):
    ended = check.get('is_ended') is not False
    failed = bool(check.get('is_failed'))
    passed = check.get('is_passed', int(check['score']) == 1)
    status = 'В обработке' if not ended else 'Ошибка' if failed else 'Пройдена' if passed else 'Не пройдена'
    row = {
        "_id": str(check["_id"]),
        "filename": check["filename"],
        "criteria": check.get("criteria", ''),
        "user": check["user"],
        "lms-username": check["user"].rsplit('_', 1)[0],
        "lms-user-id": check["lms_user_id"] if check.get("lms_user_id") else '-',
        "upload-date": (check["_id"].generation_time + timezone_offset).strftime("%d.%m.%Y %H:%M:%S"),
        "moodle-date": check['lms_passback_time'].strftime("%d.%m.%Y %H:%M:%S")
        if check.get('lms_passback_time')
        else '-',
        "score": check["score"],
        "link": f"{set_link}{url_for('results.results_main', _id=check['_id'])}" if set_link else '',
    }

    if include_status:
        row.update(is_ended=ended, is_failed=failed, is_passed=passed, status=status)
    return row
