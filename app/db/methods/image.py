import hashlib

from app.db.db_main import get_images_collection
from app.db.types.Image import Image

images_collection = get_images_collection()


def get_image(image_id):
    image = images_collection.find_one({'_id': image_id})
    if image is not None and isinstance(image.get('check_id'), str):
        image['check_id'] = [image['check_id']]
    return Image.from_document(image) if image is not None else None


def get_images_by_check_id(check_id):
    images = []
    for image in images_collection.find({'check_id': str(check_id)}):
        if isinstance(image.get('check_id'), str):
            image['check_id'] = [image['check_id']]
        image_model = Image.from_document(image)
        image_model.active_check_id = check_id
        images.append(image_model)
    return images


def calculate_image_checksum(image_data):
    return hashlib.sha256(image_data).hexdigest() if image_data else None


def is_checksum_in_db(checksum):
    return bool(checksum and images_collection.find_one({'checksum': checksum}))


def _add_check_to_existing_image(image, check_id):
    current_check_ids = image.get('check_id', [])
    if isinstance(current_check_ids, list):
        images_collection.update_one({'_id': image['_id']}, {'$addToSet': {'check_id': check_id}})
    else:
        current_check_ids = [current_check_ids] if current_check_ids else []
        if check_id not in current_check_ids:
            current_check_ids.append(check_id)
        images_collection.update_one({'_id': image['_id']}, {'$set': {'check_id': current_check_ids}})
    return image['_id']


def save_image_to_db(
    check_id,
    image_data,
    caption,
    image_size,
    document_id=None,
    text=None,
    page=None,
    checksum=None,
    text_density=None,
    symbols_percentage=None,
):
    check_id = str(check_id)
    checksum = checksum or calculate_image_checksum(image_data)
    if checksum:
        existing_image = images_collection.find_one({'checksum': checksum})
        if existing_image is not None:
            return _add_check_to_existing_image(existing_image, check_id)

    image = Image(
        check_id=[check_id],
        document_id=str(document_id) if document_id is not None else '',
        image_data=image_data,
        caption=caption,
        image_size=image_size,
        text=text,
        page=page,
        checksum=checksum,
        text_density=text_density,
        symbols_percentage=symbols_percentage,
    )
    return images_collection.insert_one(image.to_son()).inserted_id


def update_image(image):
    return bool(images_collection.find_one_and_replace({'_id': image.pk}, image.to_son()))
