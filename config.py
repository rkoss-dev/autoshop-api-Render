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
    # get this URL from Render later
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "SimpleCache"
    # Disable rate limiting during development, enable in production
    RATELIMIT_ENABLED = False
