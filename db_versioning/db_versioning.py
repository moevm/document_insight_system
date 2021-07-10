import argparse
from pymongo import MongoClient
from datetime import datetime
from versions import versions, get_version


class DBCollections:

    @classmethod
    def init(cls, mongo_url):
        cls.client = MongoClient(mongo_url)
        cls.db = cls.client['pres-parser-db']
        cls.users_collection = cls.db['users']
        cls.presentations_collection = cls.db['presentations']
        cls.checks_collection = cls.db['checks']
        cls.version_collection = cls.db['db_version']

    @classmethod
    def get_by_name(cls, name):
        return dict(
            users = cls.db['users'],
            presentations = cls.db['presentations'],
            checks = cls.db['checks']
        ).get(name)


def add_version(version):
    version_doc = DBCollections.version_collection.insert_one(version.to_dict())
    return version_doc.inserted_id

def update_db_version():
    version_doc = DBCollections.version_collection.find_one()
    
    if not version_doc:
        version_doc_id = add_version(versions[0])    # if no version == 1.0
        version_doc = DBCollections.version_collection.find_one({'_id': version_doc_id})
    version_doc_id = version_doc['_id']

    last_version = versions[-1].version
    if version_doc['version'] == last_version:
        print(f'DB have last version ({last_version})')
        exit(0)

    cur_version_name = version_doc['version']
    last_version = versions[-1]

    if cur_version_name not in last_version.changes:
        print(f"Last version {last_version.version} doesn't have changes for current {cur_version_name}")
        exit(1)

    for collection_name, changes in last_version.changes[cur_version_name].items():
        if changes:
            make_changes(DBCollections.get_by_name(collection_name), changes)

    print(f"Prev version: {version_doc}")
    DBCollections.version_collection.update({'_id': version_doc_id}, last_version.to_dict())
    print(f"New version: {DBCollections.version_collection.find_one({'_id': version_doc_id})}")

    print(f'Updated from {cur_version_name} to {last_version.version}')

def make_changes(collection, changes):
    print(collection, changes)
    collection.update_many({}, changes, False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Checks DB version, makes the necessary changes for the transition')

    parser.add_argument('--mongo', default='mongodb://mongodb:27017', help='Mongo host')
    args = parser.parse_args()

    DBCollections.init(args.mongo)
    DBCollections.version_collection.drop()

    update_db_version()
