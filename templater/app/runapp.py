import os
import configparser
import io
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from paste.deploy import loadapp
from waitress import serve
from gridfs import GridFS
from pymongo import MongoClient, DESCENDING
import datetime

def background_tasks():
    print("background task running...")
    if 'DB_PORT_27017_TCP_ADDR' in os.environ:
        db = MongoClient(
            os.environ['DB_PORT_27017_TCP_ADDR'],
            27017)['templater']
    else:
        mongo_uri = config.get('templater','mongo_uri', fallback=None)
        if mongo_uri is None:
            raise Exception("Database not found")
        else:
            db = MongoClient(mongo_uri)['templater']
    fs = GridFS(db)

    remove_old_files(fs)
    check_db_size_limit(db, fs)
    

def remove_old_files(fs):
    count = 0
    delta = datetime.timedelta(minutes=-int(config.get('templater','file_max_age',fallback='60')))
    for gridout in fs.find({'uploadDate': {'$lt' : datetime.datetime.utcnow() + delta }}):
        fs.delete(gridout._id)
        count+=1
    print("remove expired: "+str(count))


def check_db_size_limit(db, fs):
    count = 0
    total_size = 0
    limit = int(config.get('templater','db_max_size',fallback='500'))*1048576
    for item in db.fs.files.find().sort("uploadDate", DESCENDING):
        if(total_size<limit):
            total_size+=item['length']
        else:
            fs.delete(item['_id'])
            count+=1
    print("remove due to db size limit: "+str(count))


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(background_tasks,
        trigger='interval', 
        id='bg_tasks', 
        minutes=10
    )
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read('config.ini')

    atexit.register(lambda: scheduler.shutdown())

    background_tasks()

    port = int(os.environ.get("PORT", 5000))
    app = loadapp('config:production.ini', relative_to='.')

    serve(app, host='0.0.0.0', port=port)
    
