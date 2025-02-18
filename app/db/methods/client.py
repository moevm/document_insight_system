from gridfs import GridFSBucket, NoFile
from pymongo import MongoClient


client = MongoClient("mongodb://mongodb:27017")
db = client['pres-parser-db']
fs = GridFSBucket(db)


def get_client():
    return client


def get_db():
    return db


def get_fs():
    return fs