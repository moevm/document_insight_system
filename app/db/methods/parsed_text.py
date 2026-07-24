from app.db.db_main import get_files_info_collection, get_parsed_texts_collection

parsed_texts_collection = get_parsed_texts_collection()
files_info_collection = get_files_info_collection()


def add_parsed_text(file_id, parsed_text):
    result = parsed_texts_collection.update_one(
        {'filename': parsed_text.filename}, {'$set': parsed_text.pack()}, upsert=True
    )
    parsed_text_id = result.upserted_id
    if parsed_text_id is None:
        parsed_text_id = parsed_texts_collection.find_one({'filename': parsed_text.filename})['_id']
    files_info_collection.update_one({'_id': file_id}, {'$push': {'parsed_texts': parsed_text_id}})
    return parsed_text_id
