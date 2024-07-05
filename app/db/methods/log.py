import pymongo

from app.db.db_methods import get_logs_collection
from app.db.methods.client import get_client, get_db, get_fs

from app.db.types.Logs import Logs

# client = get_client()
db = get_db()
# fs = get_fs()

logs_collection = get_logs_collection()


def add_log(timestamp, serviceName, levelname, levelno, message,
            pathname, filename, funcName, lineno):
    args = locals()
    new_log = Logs(args)
    logs_collection.insert_one(new_log.pack())
    return new_log


def get_logs_cursor(filter={}, limit=10, offset=0, sort=None, order=None):
    sort = 'serviceName' if sort == 'service-name' else sort

    count = logs_collection.count_documents(filter)
    rows = logs_collection.find(filter)

    if sort and order in ("asc, desc"):
        rows = rows.sort(sort, pymongo.ASCENDING if order ==
                                                    "asc" else pymongo.DESCENDING)

    rows = rows.skip(offset) if offset else rows
    rows = rows.limit(limit) if limit else rows

    return rows, count