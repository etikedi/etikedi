from datetime import timedelta


class Config(object):
    SQLALCHEMY_DATABASE_URI = "sqlite:///testdb.db"
    DEBUG = True
    SECRET_KEY = 'ieantnqgevlngfgpznnnzpvngnfg1h08309e4ngferfpnqguivnqgh09ßengß'
    CSRF_ENABLED = False
    JWT_EXPIRATION_EDLAT = timedelta(days=10)
