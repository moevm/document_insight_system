from .timezone import timezone_offset


def format_check(check):
    grade_passback_time = check['lms_passback_time']
    grade_passback_ts = grade_passback_time.strftime(
        "%H:%M:%S - %b %d %Y") if grade_passback_time else '-'
    return (str(check['_id']), check['user'], check['filename'], check['criteria'],
            (check['_id'].generation_time + timezone_offset).strftime("%H:%M:%S - %b %d %Y"),
            grade_passback_ts, check['score'])
