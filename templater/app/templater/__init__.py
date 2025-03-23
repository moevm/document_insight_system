from pyramid.config import Configurator

import configparser
import io
import os
from webob import Response, Request
from webob.exc import HTTPBadRequest
from gridfs import GridFS
from pymongo import MongoClient

def restrict_body_middleware(app, max_size=0):
    """
    this is straight wsgi middleware and in this case only depends on
    webob. this can be used with any wsgi compliant web
    framework(which is pretty much all of them)
    """
    def m(environ, start_response):
        r = Request(environ)
        if r.content_length is None or int(r.content_length) <= max_size*1048576:
            return r.get_response(app)(environ, start_response)
        else:
            err_body = """
            request content_length(%s) exceeds
            the configured maximum content_length allowed(%s)
            """ % (r.content_length, max_size*1048576)
            res = HTTPBadRequest(err_body)
            return res(environ, start_response)

    return m

def make_application(global_config, settings, templater_config):
    """ This function returns a Pyramid WSGI application.
    """
    settings.setdefault('jinja2.i18n.domain', 'templater')
    config =  Configurator(settings=settings)
    # db_url = urlparse(settings['mongo_uri'])
    
    # config.registry.db = MongoClient(settings['mongo_uri'])


    for s in templater_config.sections():
        config.registry.settings[s] = dict(templater_config.items(s))
    if 'DB_PORT_27017_TCP_ADDR' in os.environ:
        config.registry.db = MongoClient(
            os.environ['DB_PORT_27017_TCP_ADDR'],
            27017)
    else:
        try:
            mongo_uri = config.registry.settings['templater']['mongo_uri']
            if mongo_uri is None:
                raise Exception("Database not found")
            else:
                config.registry.db = MongoClient(mongo_uri)
        except:                 
            raise Exception("Database not found")


    def add_db(request):
        db = config.registry.db['templater']
        return db

    def add_fs(request):
        return GridFS(request.db)

    config.add_request_method(add_db, 'db', reify=True)
    config.add_request_method(add_fs, 'fs', reify=True)
    
    config.add_translation_dirs('locale/')

    config.include('pyramid_jinja2')
    config.include('.routes')
    config.scan()

    return config.make_wsgi_app()


def main(global_config, **settings):
    settings = dict(settings)
    templater_config = configparser.ConfigParser()
    templater_config.read('config.ini')
    return restrict_body_middleware(make_application(global_config, settings, templater_config), int(templater_config['templater']['file_max_size']))