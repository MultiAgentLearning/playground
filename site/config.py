import os

import dj_redis_url


def cache_config():
    config = {'CACHE_TYPE':'simple'}
    REDIS_HOST = os.getenv('PLAYGROUND_REDISTOGO_URL')
    if REDIS_HOST:
        info = dj_redis_url.parse(REDIS_HOST)
        config['CACHE_TYPE'] = 'redis'
        config['CACHE_KEY_PREFIX'] = 'flask_cache'
        for key in ['HOST', 'PASSWORD', 'PORT']:
            value = info.get(key)
            if value:
                config['CACHE_KEY_' + key] = value
    print("CC")
    return config


class _BaseConfig:
    """Base configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv('PLAYGROUND_DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    GOOGLE_CLIENT_ID = os.getenv('PLAYGROUND_GOOGLE_OAUTH_CLIENT_ID')
    GOOGLE_REDIRECT_URI = os.getenv('PLAYGROUND_GOOGLE_OAUTH_REDIRECT')
    GITHUB_CLIENT_ID = os.getenv('PLAYGROUND_GITHUB_OAUTH_CLIENT_ID')
    debug = False
    console_email = False
    testing = False
    CACHE_CONFIG = cache_config()
    PLAYGROUND_BASE_URL = os.getenv('PLAYGROUND_BASE_URL', 'http://localhost:5000')

    DEFAULT_EMAIL_SENDER_NAME = "Playground"
    DEFAULT_EMAIL_SENDER_EMAIL = "cinjon@playground.com"
    DEFAULT_EMAIL_REPLYTO = "Support <support@playground.com>"

    # Keep secret
    SECRET_KEY = os.getenv('PLAYGROUND_SECRET_KEY')
    GOOGLE_CLIENT_SECRET = os.getenv('PLAYGROUND_GOOGLE_OAUTH_SECRET')
    GITHUB_CLIENT_SECRET = os.getenv('PLAYGROUND_GITHUB_OAUTH_SECRET')
    ###


class DevelopmentConfig(_BaseConfig):
    """Development configuration"""
    debug = True
    console_email = True


class TestingConfig(_BaseConfig):
    """Testing configuration"""
    debug = True
    console_email = True
    testing = True


class ProductionConfig(_BaseConfig):
    """Production configuration"""
    pass
