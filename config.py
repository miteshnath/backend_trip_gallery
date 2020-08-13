import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


POSTGRES = {
    'user': os.environ.get('PG_USER'),
    'pw': os.environ.get('PG_PW'),
    'db': os.environ.get('PG_DB'),
    'host': os.environ.get('PG_HOST'),
    'port': os.environ.get('PG_PORT'),
}

s3_bucket = os.environ.get("S3_BUCKET")
ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


class Config(object):
    DEBUG = False
    SECRET_KEY = str(os.environ.get("FLASK_KEY"))

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI


class DevelopmentConfig(Config):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
