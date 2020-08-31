"""Default configuration

Use env var to override
"""
import os

appname = __package__
basedir = os.path.abspath(os.curdir)
version = "0.0.1-alpha"

ENV = os.getenv("FLASK_ENV")
DEBUG = ENV == "development"
SECRET_KEY = os.getenv("SECRET_KEY")


def database_config():
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    return SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS


def jwt_blacklist_config():
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    return JWT_BLACKLIST_ENABLED, JWT_BLACKLIST_TOKEN_CHECKS


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY", "79a9ba1db3988b1703b05fd4d2873516")
    DNS_PREFIX = os.getenv("DNS_PREFIX", "http://192.168.5.127:8000")
    BASEDIR = basedir
    APPNAME = appname
    DEBUG = False
    TESTING = False
    VERSION = version
    PROPAGATE_EXCEPTIONS = True


class DevelopmentConfig(Config):

    ENV = "development"
    JWT_SECRET_KEY = Config.SECRET_KEY
    jwt_blacklist_config()
    SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS = database_config()
    DEBUG = True


class TestingConfig(Config):

    ENV = "testing"
    JWT_SECRET_KEY = Config.SECRET_KEY
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):

    ENV = "production"
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    DEBUG = False
    PROPAGATE_EXCEPTIONS = True


instances = dict(
    production=ProductionConfig,
    testing=TestingConfig,
    development=DevelopmentConfig,
)
