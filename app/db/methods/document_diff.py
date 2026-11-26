from app.db.db_main import get_document_diff_collection

collection = get_document_diff_collection()


def add_comparison(comparison):
    return collection.insert_one(comparison).inserted_id


def update_comparison(comparison_record_id, values):
    return collection.update_one({'_id': comparison_record_id}, {'$set': values})


def get_comparison(comparison_record_id):
    return collection.find_one({'_id': comparison_record_id})
