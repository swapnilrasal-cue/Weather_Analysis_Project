from decouple import config
from configparser import ConfigParser

config = ConfigParser()
config.read('secret.ini')

SECRET_KEY = config['settings']['SECRET_KEY']

DB_HOST = config['settings']['dbhost']
DB_USER = config['settings']['dbuser']
DB_PASS = config['settings']['dbpass']
DB_NAME = config['settings']['dbname']

conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(DB_USER, DB_PASS, DB_HOST, DB_NAME)