from urllib.parse import quote
import json

with open("/etc/secrets.json", "r") as secrets_file:
    config = json.load(secrets_file)
class Config:
    SECRET_KEY = config.get("SECRET_KEY")
    UPLOAD_FOLDER = './PrizeBondApp/static/results'
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = "587"
    MAIL_USE_TLS = "1"  
    MAIL_USERNAME = config.get("MAIL_USERNAME")
    MAIL_PASSWORD = config.get("MAIL_PASSWORD")
    ADMINS = [config.get("EMAIL")]
    SUBSCRIPTION_KEY = config.get("SUBSCRIPTION_KEY")
    ENDPOINT = config.get("ENDPOINT")
    REDIS_URL = 'redis://'

class ProductionConfig(Config):
    FLASK_ENV = "production"
    TESTING = False
    SQLALCHEMY_DATABASE_URI = f'postgresql://{config.get("DB_ROLE")}:%s@{config.get("HOST")}/{config.get("DB_NAME")}' % quote(config.get("DB_PASSWORD"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    FLASK_ENV = "development"
    FLASK_DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
