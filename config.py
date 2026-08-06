import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///autoshop.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "SimpleCache"


class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "SimpleCache"
    RATELIMIT_ENABLED = False
