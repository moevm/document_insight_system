from app.db.methods.client import get_db, get_fs


from app.db.types.Consumers import Consumers

db = get_db()
fs = get_fs()

consumers_collection = db['consumers']


# LTI
class ConsumersDBManager:

    @staticmethod
    def add_consumer(consumer_key, consumer_secret, timestamp_and_nonce=[]):
        consumer = Consumers()
        consumer.consumer_key = consumer_key
        consumer.consumer_secret = consumer_secret
        if consumers_collection.find_one({'consumer_key': consumer_key}) is not None:
            return None
        else:
            consumers_collection.insert_one(consumer.pack())
            return consumer

    @staticmethod
    def get_secret(key):
        consumer = consumers_collection.find_one({'consumer_key': key})
        if consumer is not None:
            return consumer.get('consumer_secret')
        else:
            return None

    @staticmethod
    def is_key_valid(key):
        consumer = consumers_collection.find_one({'consumer_key': key})
        if consumer is not None:
            return True
        else:
            return False

    @staticmethod
    def has_timestamp_and_nonce(key, timestamp, nonce):
        consumer = consumers_collection.find_one({'consumer_key': key})
        if consumer is not None:
            entries = consumer.get('timestamp_and_nonce')
            return (timestamp, nonce) in entries
        else:
            return False

    @staticmethod
    def add_timestamp_and_nonce(key, timestamp, nonce):
        upd_consumer = {"$push": {'timestamp_and_nonce': (timestamp, nonce)}}
        consumer = consumers_collection.update_one(
            {'consumer_key': key}, upd_consumer)
        return consumer if consumer else None