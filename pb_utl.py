#############################################
# Plazabot - pb_utl.py
# (c)2021, Doubtfull Productions
#--------------------------------------------
# Multiple utility functions
#-------------------------------------------- 
# TODO
#-------------------------------------------- 

# Getting libraries
import base64
import os
import stat
import logging
import random
import json
#import pexpect
import subprocess
import signal
import time
import requests
from datetime import datetime, timedelta
from flask import request, jsonify
from pb_config import *
from pb_db import db, Logs, Skipables
from pb_string import *
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy, ProxyType
from fake_useragent import UserAgent
from pb_clickatelly import *
from pb_gmailer import send_gmail
from pb_mailer import send_mail

# Prepping logger
logging.getLogger().setLevel(logging.INFO)

# Just some classes and functions here and there
def handle_error(func, path, exc_info):
    '''
    Handles error when trying to delete folders. Changes the actual attributes of the folder and
    its contents to allow the process to continue.
        Parameters:
            func (object): Function object
            path (string): Path for file
            exc_info (string): 
        Returns: Object
    '''
    logging.info('Handling Error for file: ' + path)
    logging.info(exc_info)
    # Check if file access issue
    if not os.access(path, os.W_OK):
       logging.info('Trying to change permission to delete the project')
       # Try to change the permision of file
       os.chmod(path, stat.S_IWUSR)
       # call the calling function again
       func(path)

def rand_string(length=5, my_haystack='ABCDEF0123456789'):
    '''
    Returns a scrambled random string with a defined length, based on a haystack of characters.
        Parameters:
            length (int): A decimal integer, default=5.
            my_haystack(string): A string source used for the random string generation, default=ABCDEF0123456789.\
        Returns: String
    '''
    return ''.join((random.choice(my_haystack) for _ in range(length)))

def err_json(daerror):
    '''
    Standarizes any error string and format it into a standard JSON object
        Parameters:
            daerror (string): String to be formatted
        Returns: Serialized object
    '''
    error_dict = {}
    error_dict.update({'error': str(daerror)})
    return json.dumps(error_dict)

def allowed_file(filename):
    '''
    Checks the filename if it has an allowed file extension.
        Parameters:
            filename (string): The filename to be checked
        Returns: Boolean
    '''
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in allowed_extensions

def folder_sanitizer(my_target):
    '''
    Sanitizes(clean) target folder of any kind of malicious or shaddy things.
        Parameters:
            my_target (string): The target folder to be scanned
        Returns: Null
    '''
    logging.info('Sanitizing...')
    # Setting all permissions to owner only
    os.chmod(my_target, stat.S_IRWXU)

def str_to_bool(s):
    if s.upper() == 'TRUE':
        return True
    elif s.upper() == 'FALSE':
        return False
    else:
        return '{}: is not boolean!'.format(s)

def log_store(log_server_uri, my_payload):
    '''
    Receives URI, payload and attached files to store results
        Parameters:
            log_server (string): Server URI
            my_payload (dict): payload dict
    '''
    response = requests.post(log_server_uri, data=my_payload)
    return response

def log_get(log_server_uri, my_payload):
    '''
    Receives URI, payload and attached files to retrieve results
        Parameters:
            log_server (string): Server URI
            my_payload (dict): payload dict
    '''
    response = requests.get(log_server_uri, data=my_payload)
    return response

def bite_me(stringo):
    s = stringo.encode('utf-8')
    return base64.b64decode(s)

def selenium_log(browser_obj, server_address, log_type, description):
    '''
    Stores log for Selenium objects depends on log_store
    Creates payload based on selenium data
        Parameters:
            browser_obj (obj): Selenium browser object
            server_address (string): Log Server URI
            log_type (string/choice): one of the std choices defined
            description (string): a brief description of the error
    '''
    screenshot =  UPLOAD_FOLDER + 'browser_error.png'
    browser_obj.save_screenshot(screenshot) # screenshot of error
    data = browser_obj.page_source
    image = open(screenshot, 'rb')
    file_byte = image.read()
    file_string = [base64.b64encode(file_byte).decode('utf-8')]

    payload = {
        'log_description' : description,
        'log_type'        : log_type,
        'log_module'      : MODULE_SELENIUM,
        'data'            : data,
        'log_image'       : file_string
    }
    response = log_store(server_address, payload)
    image.close()
    return response

def stock_check(site_data):
    '''
    Checks expected value based on 'site data' provided using selenium
        Parameters:
            site_data (dict): Dict containing site info
        Returns: Boolean
    '''

    try:
        f_lin = open('crawler_lin.lock', 'r')
        my_lin = f_lin.readlines()[0]
        f_lin.close()
    except Exception as error:
        logging.info(error)
        my_lin = '0'

    reload_config()
    bot_item = site_data[0]
    bot_url = site_data[1]
    bot_class = site_data[2]
    bot_expect = site_data[3].upper()
    amazon_fallback = site_data[3]

    display = None

    # creating skippable object, to kill if critical
    me_salto = Skipable()

    # Setting virtual display, if needed
    try:
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        logging.info('Virtual display initialized.')
        txt_msg = 'Virtual display initialized'
        da_payload = {
        'log_description' : txt_msg,
        'log_type'        : LOG_EVENT,
        'log_module'      : MODULE_SELENIUM
        }
        log_store(LOG_URI, da_payload)
    except:
        logging.info('Virtual display not needed, using gecko.')
        pass

    # Setting options
    options = Options() # mcdudas comentar
    ua = UserAgent() # mcdudas comentar
    userAgent = ua.random # mcdudas comentar
    logging.info(userAgent) # mcdudas comentar
    # Setting up Firefox/gecko
    firefox_profile = webdriver.FirefoxProfile(firefox_options=options) # mcdudas comentar
    # firefox_profile = webdriver.FirefoxProfile() # Original
    firefox_profile.set_preference('browser.download.folderList', 2)
    firefox_profile.set_preference('browser.download.manager.showWhenStarting', False)
    firefox_profile.set_preference('browser.download.dir', os.getcwd())
    firefox_profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
    # TODO Estas opciones para configurar uso de proxy (intentando con TOR pero no sirvió)
    # firefox_profile.set_preference('network.proxy.type', 1)
    # firefox_profile.set_preference('network.proxy.socks', 'localhost')
    # firefox_profile.set_preference('network.proxy.socks_port', 9150)
    # firefox_profile.set_preference('network.proxy.socks_remote_dns', True)

    firefox_profile.update_preferences()
    txt_msg = 'Firefox/Gecko profile initialization ok!'
    da_payload = {
    'log_description' : txt_msg,
    'log_type'        : LOG_EVENT,
    'log_module'      : MODULE_SELENIUM
    }
    log_store(LOG_URI, da_payload)

    # creating Selenium browser object
    browser = webdriver.Firefox(firefox_profile=firefox_profile)
    txt_msg = 'Opening url: {}'.format(bot_url)
    da_payload = {
    'log_description' : txt_msg,
    'log_type'        : LOG_EVENT,
    'log_module'      : MODULE_SELENIUM
    }
    log_store(LOG_URI, da_payload)
    logging.info('Opening %s', bot_url)
    es_amazon = False
    amazon_out = False
    if (bot_url.find('amazon.com')!=-1):
        # url es un posible amazon link
        es_amazon = True
        txt_msg = 'Possible AMAZON link found.'
        da_payload = {
        'log_description' : txt_msg,
        'log_type'        : LOG_EVENT,
        'log_module'      : MODULE_SELENIUM
        }
        log_store(LOG_URI, da_payload)

    browser.get(bot_url)
    now = time.time()
    bailer = 0
    while True:
        try:
            if es_amazon:
                WebDriverWait(browser, WAIT_TIMEOUT).until(
                    expected_conditions.presence_of_element_located((By.ID, bot_class))
                )
                logging.info('No Stock!')
                selenium_log(browser, LOG_URI, LOG_ALERT, 'Amazon class {} found!'.format(bot_class))
                amazon_out = True
                break
            else:
                WebDriverWait(browser, WAIT_TIMEOUT).until(
                    expected_conditions.presence_of_element_located((By.CLASS_NAME, bot_class))
                )
            bot_stock = browser.find_element_by_class_name(bot_class).text.upper()
            if (len(bot_stock)<=3):
                logging.info('Class found but empty!')
                selenium_log(browser, LOG_URI, LOG_WARNING, 'Class {} found but empty: {}'.format(bot_class, bot_stock))
                break            
            logging.info('Comparando expect: {} vs. en sitio: {} <<<<<<<<<<<<<<<<<<<<<<<<<'.format(bot_expect, bot_stock))
            strlocator = bot_stock.find(bot_expect)
            if (strlocator == -1):
                logging.info('Found!')
                selenium_log(browser, LOG_URI, LOG_SUCCESS, 'Item () found!'.format(bot_item))
                return True
            break
        except Exception as e:
            if es_amazon:
                amazon_out = False
                break
            bailer += 1
            error_msg = 'Class {} not found retry {} of 3. Possible bailing - {}.'.format(bot_class, bailer, e)
            logging.info(error_msg)
            da_payload = {
            'log_description' : error_msg,
            'log_type'        : LOG_ALERT,
            'log_module'      : MODULE_SELENIUM
            }
            log_store(LOG_URI, da_payload)
            if bailer >= 3:
                logging.info('Bailing... dammit!')
                bailing_error = 'Fallo sitio {} para item {}. No existe class {}'.format(bot_url, bot_item, bot_class)
                logging.info('Notifiying')
                notifier(bailing_error)
                selenium_log(browser, LOG_URI, LOG_CRITICAL, bailing_error)
                me_salto.skip(my_lin) # critical error killing line for x time
                break
            time.sleep(1)
    
    if es_amazon:
        if not amazon_out:
            try:
                WebDriverWait(browser, WAIT_TIMEOUT).until(
                    expected_conditions.presence_of_element_located((By.ID, amazon_fallback))
                )
                logging.info('No Stock!')
                selenium_log(browser, LOG_URI, LOG_ALERT, 'Amazon class {} found!'.format(amazon_fallback))
            except Exception as e:
                logging.info('Amazon: Found!... Maybe?')
                selenium_log(browser, LOG_URI, LOG_SUCCESS, 'Amazon item {} found, maybe?\nGo to url: {}'.format(bot_item, bot_url))
                return True     

    # Browser destroy
    browser.quit()
    try:
        display.stop()
    except:
        pass
    logging.info('Not Found!')
    log_payload = {
        'log_description' : 'Item {} not found'.format(bot_item),
        'log_type'        : LOG_ALERT,
        'log_module'      : MODULE_SELENIUM,
        'data'            : 'Item Url:{}\nItem class:{}\nItem class value: {}'.format(bot_url,bot_class,bot_expect)
    }
    log_store(LOG_URI, log_payload)
    return False

def notifier(bot_text):
    '''
    Notifies to multiple targets
        Parameters:
            bot_text : (string) Text to notify
        Returns: Null
    '''
    reload_config()
    # First, slack
    if (NOTIFIER_ABLE[0]==1):
        bot_slack = SLACK_URL
        payload = { 
            "text" : bot_text
        }
        response = requests.post(bot_slack, json = payload)
        if (response.status_code != 200):
            logging.info('Status {} - {}'.format(response.status_code, response.text))
            txt_msg = 'Slack Error: {} - {}'.format(response.status_code, response.text)
            da_payload = {
            'log_description' : txt_msg,
            'log_type'        : LOG_ERROR,
            'log_module'      : MODULE_NOTIFIER,
            'data'            : txt_msg
            }
            log_store(LOG_URI, da_payload)

    for target_no in SMS_TARGET:
        # Second SMS
        if (NOTIFIER_ABLE[1]==1):
            try:
                response = send_sms(target_no, bot_text )
            except Exception as e:
                logging.info('CLICKATELL sms error: {}'.format(e))
                log_payload = {
                    'log_description' : 'SMS error',
                    'log_type'        : LOG_ERROR,
                    'log_module'      : MODULE_NOTIFIER,
                    'data'            : 'SMS error: {e}'.format(e)
                }
                log_store(LOG_URI, log_payload)
    
        # Third WA
        if (NOTIFIER_ABLE[2]==1):
            try:
                response = send_whatsapp(target_no, bot_text )
            except Exception as e:
                logging.info('CLICKATELL whatsapp error: {}'.format(e))
                log_payload = {
                    'log_description' : 'Whatsapp error',
                    'log_type'        : LOG_ERROR,
                    'log_module'      : MODULE_NOTIFIER,
                    'data'            : 'Whatsapp error: {}'.format(e)
                }
                log_store(LOG_URI, log_payload)
    
    # Fourth mail
    if (NOTIFIER_ABLE[3]==1):
        response = send_mail(MAIL_FROM, MAIL_TO, BOT_SUBJECT + bot_text[0:10] + '...', bot_text, BOT_SMTP_SERVER, BOT_SMTP_AUTH )
        if (response[1]==404):
            logging.info('>>>>>>>>>> ' + response[0])
            log_payload = {
                'log_description' : 'Mail error',
                'log_type'        : LOG_ERROR,
                'log_module'      : MODULE_NOTIFIER,
                'data'            : 'Mail error: {} - {}'.format(response[0], response[1])
            }
            log_store(LOG_URI, log_payload)

    # Fifth mail to SMS
    if (NOTIFIER_ABLE[4]==1):
        for target_no in SMS_MAILER:
            try:
                send_gmail('rplaza@gmail.com', SMS_MAILER, bot_text, bot_text)
            except Exception as error:
                logging.info('GMail to sms error: {}'.format(error))
                log_payload = {
                    'log_description' : 'GMail to SMS error',
                    'log_type'        : LOG_ERROR,
                    'log_module'      : MODULE_NOTIFIER,
                    'data'            : 'GMail to SMS error: {}'.format(error)
                }
                log_store(LOG_URI, log_payload)

    # Sixth Signal!
    if (NOTIFIER_ABLE[5]==1):
        signal_payload = {
            'from'      : SIGNAL_FROM,
            'msg'   : bot_text
        }
        logging.info(signal_payload)
        response = log_store(DEFAULT_URL + 'Signal/send/', signal_payload)
        logging.info(response)
        if (response.status_code==400):
            logging.info('>>>>>>>>>> ' + response[0])
            log_payload = {
                'log_description' : 'Signal error',
                'log_type'        : LOG_ERROR,
                'log_module'      : MODULE_NOTIFIER,
                'data'            : 'Signal error: {} - {}'.format(response[0], response[1])
            }
            log_store(LOG_URI, log_payload)
        

#
# Skipables object
#
class Skipable(object):
    def check(self, line):
        skip_vector = Skipables.query.filter_by(line=line).first()
        if (skip_vector is None):
            return False
        else:
            return True

    def skip(self, line):
        reload_config()
        my_skip = Skipable()
        skipeado = my_skip.check(line)
        if (not skipeado):
            current_time = datetime.now()
            minutes_added = timedelta(minutes=POPUP_TO)
            until_value = current_time + minutes_added
            new_skip = Skipables(None, line, until_value)
            db.session.add(new_skip)
            db.session.commit()
            txt_msg = 'Item line {} skipped until {}'.format(line, dump_datetime(until_value))
            da_payload = {
            'log_description' : txt_msg,
            'log_type'        : LOG_ALERT,
            'log_module'      : MODULE_DB
            }
            log_store(LOG_URI, da_payload)
            return True
        return False

    def expire(self, line):
        reload_config()
        my_skip = Skipable()
        skipeado = my_skip.check(line)
        if (skipeado):
            current_time = twotimes(dump_datetime(datetime.now()))
            skip_vector = Skipables.query.filter_by(line=line).first()
            until_time = twotimes(dump_datetime(skip_vector.until))
            if (current_time > until_time):
                db.session.delete(skip_vector)
                db.session.commit()
                txt_msg = 'Item line {} restored! Skip expired!'.format(line)
                da_payload = {
                'log_description' : txt_msg,
                'log_type'        : LOG_ALERT,
                'log_module'      : MODULE_DB
                }
                log_store(LOG_URI, da_payload)
                return True
        return False

    def clean(self):
        reload_config()
        Skipables.query.delete()
        db.session.commit()
        txt_msg = 'User triggered clean skipables.'
        da_payload = {
        'log_description' : txt_msg,
        'log_type'        : LOG_ALERT,
        'log_module'      : MODULE_DB
        }
        log_store(LOG_URI, da_payload)
        return True

#
# Child app object
#
class ChildApp:
    Is_running = False
    Name = None
    crawler = None

    @classmethod
    def toggle(cls, name):
        '''
        Starts/Stops script
            Parameters:
                name (string): Python script to be run
        '''
        reload_config()
        if (cls.Is_running):
            '''
            Stops script
            '''
            os.killpg(os.getpgid(cls.crawler.pid), signal.SIGTERM)
            cls.crawler, cls.Is_running = None, False
            txt_msg = '****** Crawler Stopping ******'
            da_payload = {
            'log_description' : txt_msg,
            'log_type'        : LOG_EVENT,
            'log_module'      : MODULE_CRAWLER,
            'data'            : txt_msg
            }
            log_store(LOG_URI, da_payload)
            return 'Crawler stopping...', 200
        else:
            '''
            Starts script
            '''
            cls.Name = name
            crawling = subprocess.Popen('python3 ' + name, stdout=subprocess.PIPE, \
                shell=True, preexec_fn=os.setsid)
            cls.crawler = crawling
            cls.Is_running = True
            txt_msg = '****** Crawler Starting ******'
            da_payload = {
            'log_description' : txt_msg,
            'log_type'        : LOG_EVENT,
            'log_module'      : MODULE_CRAWLER,
            'data'            : txt_msg
            }
            log_store(LOG_URI, da_payload)
            return 'Crawler starting...', 200

    @classmethod
    def status(self):
        '''
        Gets status of script
        '''
        my_status = 'is not'
        if (self.Is_running):
            my_status = 'is'

        return 'Crawler {} running...'.format(my_status), self.Is_running, 200

#
#  Item Class Objects
#
class ZItem(object):
    def open(self):
        file = open('z_items.cfg', 'r')
        lines = file.readlines()
        clean_file=[]
        for line in lines:
            data = line.rstrip('\r\n')
            clean_file.append(data)
        file.close()
        return json.dumps(clean_file)

    def save(self):
        reload_config()
        file = open('z_items.cfg', 'w+') 
        text = request.form.get('config_data')
        textdict = json.loads(text)
        for line in textdict:
            file.write(line + "\r\n") 
        file.close()
        txt_msg = '****** Items file updated ******'
        da_payload = {
        'log_description' : txt_msg,
        'log_type'        : LOG_EVENT,
        'log_module'      : MODULE_DB,
        'data'            : txt_msg
        }
        log_store(LOG_URI, da_payload)
        return True

#
#  Config Class Objects
#
class ZConfig(object):
    def open(self):
        file = open('settings.ini', 'r')
        lines = file.readlines()
        clean_file=[]
        for line in lines:
            data = line.rstrip('\r\n')
            clean_file.append(data)
        file.close()
        return json.dumps(clean_file)

    def save(self):
        reload_config()
        file = open('settings.ini', 'w+') 
        text = request.form.get('config_data')
        textdict = json.loads(text)
        for line in textdict:
            file.write(line + "\r\n") 
        file.close()
        txt_msg = '****** Config file updated ******'
        da_payload = {
        'log_description' : txt_msg,
        'log_type'        : LOG_EVENT,
        'log_module'      : MODULE_DB,
        'data'            : txt_msg
        }
        log_store(LOG_URI, da_payload)
        reload_config()
        txt_msg = '!=== Config file reloaded'
        da_payload = {
        'log_description' : txt_msg,
        'log_type'        : LOG_EVENT,
        'log_module'      : MODULE_DB,
        'data'            : txt_msg
        }
        log_store(LOG_URI, da_payload)
        return True

#
# Zcrawler status file
#
class CrawlerLocker(object):
    def status(self):
        my_run = '0'
        my_lin = '0'
        try:
            f_run = open('crawler_run.lock', 'r')
            my_run = f_run.readlines()[0]
            f_run.close()
        except Exception as error:
            logging.info(error)
        try:
            f_lin = open('crawler_lin.lock', 'r')
            my_lin = f_lin.readlines()[0]
            f_lin.close()
        except Exception as error:
            logging.info(error)
        response = []
        response.append(my_run)
        response.append(my_lin)
        return json.dumps(response)

#
# Signal Class Objects
#

class Signaling(object):
    def link(self):
        url_path = SIGNAL_URI + 'v1/qrcodelink?device_name={}'.format(SIGNAL_OBJ)
        logging.info(url_path)
        response = requests.get(url_path)
        return response.content

    def register(self, phone_number):
        voice_call = request.form.get('use_voice')
        logging.info(voice_call)
        url_path = SIGNAL_URI + 'v1/register/{}'.format(phone_number)
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/plain"
        }
        my_data = {
            'use_voice' : voice_call
        }
        response = requests.post(url_path, headers=headers, data=json.dumps(my_data))
        return response.text, response.status_code

    def activate(self, phone_number, code):
        url_path = SIGNAL_URI + 'v1/register/{}/verify/{}'.format(phone_number, code)
        response = requests.post(url_path)
        return response.text, response.status_code

    def send(self):
        signal_from = request.form.get('from')
        signal_to = SIGNAL_RECIPIENTS
        signal_msg = request.form.get('msg')

        url_path = SIGNAL_URI + 'v2/send'
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/plain"
        }

        data = {
            'number'    : signal_from,
            'recipients': signal_to,
            'message'   : signal_msg
        }

        response = requests.post(url_path, headers=headers, data=json.dumps(data) )
        if (response.status_code==201):
            return True
        else:
            return response.text, response.status_code

#
# LOG Class Objects
#
class LogObj(object):
    def log_list(self):
        '''
        Returns a list of available logs

        '''
        keyword = request.args.get('keyword')
        log_type = request.args.get('log_type')
        log_order = request.args.get('log_order')
        log_limit = request.args.get('log_limit')
        keyword = '' if (keyword is None) else keyword
        search = '%{}%'.format(keyword)
        
        if (log_type != LOG_ALL):
            if (log_order == LOG_SORT_ASC):
                log_vector = Logs.query.with_entities(Logs.id, Logs.timestamp, Logs.type, Logs.module, Logs.description).filter(Logs.data.like(search) & (Logs.type == log_type)).order_by(Logs.id.asc()).limit(log_limit).all()
            else:
                log_vector = Logs.query.with_entities(Logs.id, Logs.timestamp, Logs.type, Logs.module, Logs.description).filter(Logs.data.like(search) & (Logs.type == log_type)).order_by(Logs.id.desc()).limit(log_limit).all()
        else:
            if (log_order == LOG_SORT_ASC):
                log_vector = Logs.query.with_entities(Logs.id, Logs.timestamp, Logs.type, Logs.module, Logs.description).order_by(Logs.id.asc()).limit(log_limit).all()
            else:
                log_vector = Logs.query.with_entities(Logs.id, Logs.timestamp, Logs.type, Logs.module, Logs.description).order_by(Logs.id.desc()).limit(log_limit).all()

        result = {}

        if log_vector is not None:
            result =  jsonify(json_list = [i for i in log_vector]).json
        else:
            return 'No Logs found', 404
        
        return result['json_list'], 200

    def log_detail(self, log_id):
        '''
        Returns details from log

        '''
        if log_id is None:
            return DEF_PKER, 404

        log_vector = Logs.query.filter_by(id=log_id).first()

        if log_vector is not None:
            response = log_vector.serialize
            return response, 200
        else:
            return 'Log id:{} not found'.format(log_id), 404

    def log_store(self):
        '''
        Stores into log
        '''
        log_desc = request.form.get('log_description')
        log_type = request.form.get('log_type')
        log_modu = request.form.get('log_module')
        log_data = request.form.get('data')
        image = request.form.get('log_image')
        log_time = datetime.strptime(get_timestamp(),'%Y-%m-%d %H:%M:%S') # Getting timestamp

        # Creating new insert
        new_log = Logs(None, log_time, log_type, log_modu, log_desc, log_data, image)
        db.session.add(new_log)
        try:
            db.session.commit()
            result = {'Response':'[LOG][{}][{}]: {}'.format(log_type, log_time, log_desc)}
        except Exception as e:
            try:
                return {'Error': e}, 404
            except Exception as error:
                logging.info('e = {} - error = {}'.format(e,error))
                return None
        return result, 201


#############################################
# EoF
