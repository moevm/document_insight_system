import argparse

from pymongo import MongoClient

from versions import LAST_VERSION, VERSIONS


class DBCollections:
    MONGO_URL = ''

    def __new__(cls, db_name="dis-db", files_collection='files'):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBCollections, cls).__new__(cls)
            cls.instance.init(db_name, files_collection)
        return cls.instance

    def init(self, db_name, files_collection):
        self.client = MongoClient(self.MONGO_URL)
        self.db = self.client[db_name]
        self.users = self.db['users']
        self.files = self.db[files_collection]
        self.checks = self.db['checks']
        self.criteria_pack = self.db['criteria_pack']
        self.db_version = self.db['db_version']

    def get_by_name(self, name):
        return dict(
            users=self.users,
            files=self.files,
            checks=self.checks,
            criteria_pack=self.criteria_pack
        ).get(name)

    def to_dict(self):
        return vars(self)


def add_version(version):
    version_doc = DBCollections().db_version.insert_one(version.to_dict())
    return version_doc.inserted_id


def update_db_version():
    version_doc = DBCollections().db_version.find_one()

    if not version_doc:
        version_doc_id = add_version(VERSIONS[LAST_VERSION])  # if no version == LAST_VERSION
        version_doc = DBCollections().db_version.find_one({'_id': version_doc_id})
    version_doc_id = version_doc['_id']

    last_version = VERSIONS[LAST_VERSION]
    if version_doc['version'] == last_version.VERSION_NAME:
        print(f'DB has the latest version ({last_version})')
        exit(0)

    cur_version_name = version_doc['version']

    last_version.update_database(DBCollections().to_dict(), cur_version_name)

    print(f"Prev version: {version_doc}")
    DBCollections().db_version.update({'_id': version_doc_id}, last_version.to_dict())
    print(f"New version: {DBCollections().db_version.find_one({'_id': version_doc_id})}")

    print(f'Updated from {cur_version_name} to {last_version.VERSION_NAME}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Checks DB version, makes the necessary changes for the transition')

    parser.add_argument('--mongo', default='mongodb://mongodb:27017', help='Mongo host')
    args = parser.parse_args()

    DBCollections.MONGO_URL = args.mongo

    if LAST_VERSION < '4.0':
        DBCollections(db_name='pres-parser-db', files_collection='presentation')
    else:
        DBCollections()

    update_db_version()
