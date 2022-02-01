#############################################
# Plazabot - pb_config.py
# (c)2021, Doubtfull Productions
#--------------------------------------------
# Master config file
#-------------------------------------------- 
# TODO
#-------------------------------------------- 
import os, sys
import configparser
from datetime import datetime
from flask import Flask

# Initializing
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    APPLICATION_PATH = sys._MEIPASS # pylint: disable=no-member
else:
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))

# Setting up main paths for operation.
UPLOAD_FOLDER = APPLICATION_PATH + '/uploads/'

# Defining allowed extensions
allowed_extensions = {'png'}

# Create the application instance
app = Flask(__name__)

# Extra configs to secure app
# app.config['SECRET_KEY'] = os.urandom(12)
# csrf = CSRFProtect()
# csrf.init_app(app)

# Setting app upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setting Database Connection URI
# First will look for OS environment variable
# if not it will fallback to SQLite
try:
    DATABASE_CONN = os.environ['DATABASE_URI']
except:
    DATABASE_CONN = None
if ( DATABASE_CONN is None ):
    DATABASE_CONN = 'sqlite:///' + os.path.join(APPLICATION_PATH, 'plazabot.db')
app.config['SQLALCHEMY_DATABASE_URI'] =  DATABASE_CONN

# Some usefull functions
def get_timestamp():
    '''
    Just a simple function to retrieve a formatted timestamp.
    '''
    return datetime.now().strftime(('%Y-%m-%d %H:%M:%S'))

def dump_datetime(value):
    '''
    Deserialize datetime object into string form for JSON processing
    '''
    if value is None:
        return None
    return value.strftime("%Y-%m-%d %H:%M:%S")

def twotimes(value):
    if value is None:
        return None
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

global URL_CALLER

URL_CALLER = 'window.location.origin'

global WAIT_TRY, WAIT_TIMEOUT, WAIT_BETWEEN, POPUP_TO, \
    SLACK_URL, MAIL_FROM, MAIL_TO, BOT_SMTP_SERVER, BOT_SMTP_AUTH, \
    BOT_SUBJECT, SMS_TARGET, SMS_MAILER, NOTIFIER_ABLE, \
    DEFAULT_URL, LOG_URI, PUBLISHED_PORT, REQ_TABLE, REQ_CRAWLER, \
    CLICKATELL_URI, CLICKATELL_AUTH, CLICKATELL_CHAN, SIGNAL_URI, \
    SIGNAL_OBJ, SIGNAL_RECIPIENTS, SIGNAL_FROM

# Default config items this will be override by settings.ini
DEFAULT_URL = "http://localhost:5123/"
# Defaultg values for API
LOG_URI = "http://localhost:5123/Log/"
PUBLISHED_PORT = 5123
WAIT_TRY = 60 # Segundos entre corridas
WAIT_TIMEOUT = 2 # Segundos entre esperas de objeto class
WAIT_BETWEEN = 10 # Segundos entre chequeos por lista
POPUP_TO =  60 # Pausa para skip si encuentra en minutos
SLACK_URL = 'https://hooks.slack.com/services/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' # url string de slack
MAIL_FROM = 'stock.crawler@raskitoma.com'
MAIL_TO = 'rplaza@gmail.com, wantan@gmail.com'
BOT_SMTP_SERVER = 'smtp.zoho.com:587'
BOT_SMTP_AUTH = '!sL3FT8aU!hUFr'
BOT_SUBJECT = '[stock.crawler] Alert - '
SMS_TARGET = ['13055628823','593995956133']
SMS_MAILER = ['3055628823@tmomail.net']
NOTIFIER_ABLE = [0,0,0,0,0]
REQ_TABLE = 2500
REQ_CRAWLER = 2500
CLICKATELL_URI = 'https://platform.clickatell.com/v1/message'
CLICKATELL_AUTH = 'G7-ns9FPRK6UKjYyHDjepQ=='
CLICKATELL_CHAN = ['sms','whatsapp']
SIGNAL_URI = 'http://localhost:8080/'
SIGNAL_OBJ = 'PB Crawler'
SIGNAL_RECIPIENTS = ["+593995956133"]
SIGNAL_FROM = '+17869714703'

global config
config = configparser.ConfigParser()
config.read(APPLICATION_PATH + '/settings.ini')

def reload_config():
    global WAIT_TRY, WAIT_TIMEOUT, WAIT_BETWEEN, POPUP_TO, \
        SLACK_URL, MAIL_FROM, MAIL_TO, BOT_SMTP_SERVER, BOT_SMTP_AUTH, \
        BOT_SUBJECT, SMS_TARGET, SMS_MAILER, NOTIFIER_ABLE, \
        DEFAULT_URL, LOG_URI, PUBLISHED_PORT, REQ_TABLE, REQ_CRAWLER, \
        CLICKATELL_URI, CLICKATELL_AUTH, CLICKATELL_CHAN, SIGNAL_URI, \
        SIGNAL_OBJ, SIGNAL_RECIPIENTS, SIGNAL_FROM

    DEFAULT_URL = config['SERVER']['DEFAULT_URL']
    LOG_URI = config['SERVER']['LOG_URI']
    PUBLISHED_PORT = int(config['SERVER']['PUBLISHED_PORT'])
    WAIT_TRY = int(config['TIMERS']['WAIT_TRY'])
    WAIT_TIMEOUT = int(config['TIMERS']['WAIT_TIMEOUT'])
    WAIT_BETWEEN = int(config['TIMERS']['WAIT_BETWEEN'])
    POPUP_TO =  int(config['TIMERS']['POPUP_TO'])
    SLACK_URL = config['NOTIFIERS']['SLACK_URL']
    MAIL_FROM = config['NOTIFIERS']['MAIL_FROM']
    MAIL_TO = config['NOTIFIERS']['MAIL_TO']
    BOT_SMTP_SERVER = config['NOTIFIERS']['BOT_SMTP_SERVER']
    BOT_SMTP_AUTH = config['NOTIFIERS']['BOT_SMTP_AUTH']
    BOT_SUBJECT = config['NOTIFIERS']['BOT_SUBJECT']
    SMS_TARGET = config['NOTIFIERS']['SMS_TARGET'].split(',')
    SMS_MAILER = config['NOTIFIERS']['SMS_MAILER']
    NOTIFIER_ABLE = list(map(int, config['NOTIFIERS']['NOTIFIER_ABLE'].split(',')))
    REQ_TABLE = int(config['FRONTEND']['REQ_TABLE'])
    REQ_CRAWLER = int(config['FRONTEND']['REQ_CRAWLER'])
    CLICKATELL_URI = config['CLICKATELL']['URI']
    CLICKATELL_AUTH = config['CLICKATELL']['API_AUTH']
    CLICKATELL_CHAN = config['CLICKATELL']['CHANNELS'].split(',')
    SIGNAL_URI = config['SIGNAL']['URI']
    SIGNAL_OBJ = config['SIGNAL']['OBJ']
    SIGNAL_RECIPIENTS = config['SIGNAL']['RECIPIENTS'].split(',')
    SIGNAL_FROM = config['SIGNAL']['FROM']

reload_config()
#############################################
# EoF