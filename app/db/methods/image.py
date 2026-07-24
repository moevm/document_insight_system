from app.db.db_main import get_images_collection
from app.db.types.Image import Image

images_collection = get_images_collection()


def get_images(check_id):
    return [Image(image) for image in images_collection.find({'check_id': str(check_id)})]


def save_image_to_db(check_id, image_data, caption, image_size=None, text=None, page=None):
    image = Image(
        {
            'check_id': check_id,
            'image_data': image_data,
            'caption': caption,
            'image_size': image_size,
            'text': text,
            'page': page,
        }
    )
    return images_collection.insert_one(image.pack()).inserted_id


def update_image(image):
    return bool(images_collection.find_one_and_replace({'_id': image._id}, image.pack()))
