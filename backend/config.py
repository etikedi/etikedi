from datetime import timedelta


class Config(object):
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    SECRET_KEY = "ieantnqgevlngfgpznnnzpvngnfg1h08309e4ngferfpnqguivnqgh09ßengß"
    CSRF_ENABLED = False
    JWT_EXPIRATION_EDLAT = timedelta(days=10)
