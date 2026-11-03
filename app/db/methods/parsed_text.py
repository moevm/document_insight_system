from app.db.db_main import get_parsed_texts_collection
from app.db.types.ParsedText import ParsedText

parsed_texts_collection = get_parsed_texts_collection()


def get_or_create_parsed_text_id(filename):
    parsed_text = parsed_texts_collection.find_one({'filename': filename}, {'_id': 1})
    if parsed_text is not None:
        return parsed_text['_id']

    result = parsed_texts_collection.update_one(
        {'filename': filename},
        {'$setOnInsert': {'filename': filename, 'parsed_chapters': []}},
        upsert=True,
    )
    return result.upserted_id or parsed_texts_collection.find_one({'filename': filename}, {'_id': 1})['_id']


def save_parsed_text(check_id, parsed_text, document_id=None):
    if not isinstance(parsed_text, ParsedText):
        parsed_text = ParsedText(**parsed_text)
    parsed_text_id = document_id or get_or_create_parsed_text_id(parsed_text.filename)
    parsed_text_data = parsed_text.to_son()
    parsed_text_data.pop('_id', None)
    parsed_texts_collection.update_one({'_id': parsed_text_id}, {'$set': parsed_text_data})
    return parsed_text_id
