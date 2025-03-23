import os
from sqlalchemy import create_engine

import urllib

class Config(object):
    SECRET_KEY='Key Nueva'
    SESSION_COOKIE_SECRET=False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Root@127.0.0.1/pizzas_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    