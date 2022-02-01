#############################################
# Plazabot - pb_api.py
# (c)2021, Doubtfull Productions
#--------------------------------------------
# Master api endpoint file
#-------------------------------------------- 
# TODO 
#-------------------------------------------- 

# Getting libraries
from flask_restx import Api, Resource, reqparse
from werkzeug.middleware.proxy_fix import ProxyFix
from pb_config import app, PUBLISHED_PORT, \
    REQ_TABLE, REQ_CRAWLER, URL_CALLER
from pb_utl import LogObj, ChildApp, ZItem, bite_me, \
    CrawlerLocker, Skipable, ZConfig, Signaling
from pb_string import *
from flask import render_template, make_response

# Default frontend
@app.route('/')
def index():
    response = make_response(render_template('pb_fe.html', \
        base_root = URL_CALLER, req_table = REQ_TABLE, req_crawler = REQ_CRAWLER))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/img/<log_id>')
def imagemaster(log_id):
    obj_log = LogObj()
    ImgObj = obj_log.log_detail(log_id)
    la_imagen = bite_me(ImgObj[0]['image'])
    return la_imagen, 200, { \
        'Access-Control-Allow-Origin': '*', \
        'Content-Type': 'image/png' \
    }

@app.route('/data/<log_id>')
def datamaster(log_id):
    obj_log = LogObj()
    DataObj = obj_log.log_detail(log_id)
    la_data = DataObj[0]['data']
    return la_data, 200, { \
        'Access-Control-Allow-Origin': '*', \
        'Content-Type': 'text/html' \
    }

@app.route('/link/')
def qr_code():
    obj_qr_code = Signaling()
    qr_codex = obj_qr_code.link()
    return qr_codex, 200, { \
        'Access-Control-Allow-Origin': '*', \
        'Content-Type': 'image/png' \
    }
    
# Creating api
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app,
    version='1.0.0-a',
    title='Plazabot-API',
    endpoint='/api',
    doc='/api',
    description='Plazabot API - API Entrypoint for configuration/request/maintenance'
)

# Defining Namespace
ns1 = api.namespace('Log', description='Log operations')
ns2 = api.namespace('Crawler', description='Crawler Control Operations')
ns3 = api.namespace('Maintenance', description='System maintenance')
ns4 = api.namespace('Signal', description='Signal API connection')

# Defining parser objects with custom headers, etc.
# Object for searcher
searcher_parser = reqparse.RequestParser()
searcher_parser.add_argument('keyword', help='Keyword', location='query', default=None)
searcher_parser.add_argument('log_type', help='Log Type', location='query', \
    choices=(LOG_ALL, LOG_ALERT, LOG_ERROR, LOG_SUCCESS, LOG_WARNING, LOG_EVENT, LOG_CRITICAL), \
    required = True )
searcher_parser.add_argument('log_order', help='DateTime Order', location='query', \
    choices=(LOG_SORT_ASC, LOG_SORT_DES), default = LOG_SORT_DES, \
    required = True )
searcher_parser.add_argument('log_limit', help='How many lines of log to retrieve', location='query', \
    required = True, default = 100 )

# object for new LOG
new_log = reqparse.RequestParser()
new_log.add_argument('log_description', help='Log Description', location='form', required = True)
new_log.add_argument('log_type', help='Log Type', location='form', \
    choices=(LOG_ALL, LOG_ALERT, LOG_ERROR, LOG_SUCCESS, LOG_WARNING, LOG_EVENT, LOG_CRITICAL), \
    default = LOG_EVENT, required = True )
new_log.add_argument('log_module', help='Log Module', location='form', \
    choices=(MODULE_CRAWLER, MODULE_EVENT, MODULE_COMMS, MODULE_BROWSER, MODULE_DB, MODULE_MAILER, MODULE_NOTIFIER, MODULE_SELENIUM), \
    default = MODULE_EVENT, required = True)
new_log.add_argument('data', help='Extra associated std data', location='form', default=None)
new_log.add_argument('log_image', help='Log Screenshot if available', location='form',default=None)

# object for results request
results_parser = reqparse.RequestParser()
results_parser.add_argument('res_type', help='Type of result', default=None)
results_parser.add_argument('res_order', help='Datetime ordering', \
    choices=('asc', 'desc'), \
    default='desc' )

# object for config storage...
config_parser = reqparse.RequestParser()
config_parser.add_argument('config_data', help='Config data', location='form',required=True)

# object for signal...
signal_activation = reqparse.RequestParser()
signal_activation.add_argument('use_voice', help='Use voice call to receive activation code?', \
    choices=(True,False), \
    default=False, location='form',
    required=True )

signal_message = reqparse.RequestParser()
signal_message.add_argument('from', help='Signal sender', location='form', required=True )
signal_message.add_argument('msg', help='Message', location='form', required=True)

# Creating Child object
Child_1 = ChildApp()

@ns1.route('/')
@ns1.response(200, 'Details retrieved')
@ns1.response(201, 'Log created')
@ns1.response(202, 'Processing...')
@ns1.response(400, 'Bad syntax or data')
@ns1.response(404, 'Log not found')
class ApiLogs(Resource):
    '''
    Basic Logs management entrypoints
    '''
    @ns1.doc('log_listing')
    @ns1.expect(searcher_parser)
    def get(self):
        '''
        List all Logs available
        '''
        return LogObj.log_list(self), {'Access-Control-Allow-Origin': '*'}

    @ns1.doc('create_new_log')
    @ns1.expect(new_log)
    def post(self):
        '''
        Create a new log entry
        '''
        return LogObj.log_store(self), {'Access-Control-Allow-Origin': '*'}

@ns1.route('/<string:log_id>/')
@ns1.response(200, 'Details retrieved')
@ns1.response(404, 'Log not found')
@ns1.param('log_id', 'Log_id', required=True)
class ApiLog(Resource):
    '''
    Multiple log operations based on log id
    '''
    @ns1.doc('get_info')
    def get(self, log_id):
        '''
        Fetch log details given its id
        '''
        return LogObj.log_detail(self, log_id), {'Access-Control-Allow-Origin': '*'}

@ns2.route('/')
@ns2.response(200, 'Conn Ok')
class ApiCrawler(Resource):
    @ns2.doc('status')
    def get(self):
        return Child_1.status(), {'Access-Control-Allow-Origin': '*'}
    def post(self):
        return Child_1.toggle('pb_crawler.py'), {'Access-Control-Allow-Origin': '*'}

@ns2.route('/status/')
class CrawlerLock(Resource):
    def get(self):
        return CrawlerLocker.status(self), {'Access-Control-Allow-Origin': '*'}

@ns3.route('/Items/')
class ItemsFile(Resource):
    def get(self):
        return ZItem.open(self), {'Access-Control-Allow-Origin': '*'}
    @ns3.expect(config_parser)
    def post(self):
        return ZItem.save(self), {'Access-Control-Allow-Origin': '*'}
        
@ns3.route('/Skip/<int:line>/')
class Skipme(Resource):
    def get(self, line):
        return Skipable.check(self, line), {'Access-Control-Allow-Origin': '*'}

    def post(self, line):
        return Skipable.skip(self, line), {'Access-Control-Allow-Origin': '*'}

@ns3.route('/Skip/<int:line>/delete/')
class Skipme_del(Resource):
    def post(self, line):
        return Skipable.expire(self, line), {'Access-Control-Allow-Origin': '*'}

@ns3.route('/Skip/Clean/')
class Skipme_kill(Resource):
    def post(self):
        return Skipable.clean(self), {'Access-Control-Allow-Origin': '*'}

@ns3.route('/Config/')
class ConfigFile(Resource):
    def get(self):
        return ZConfig.open(self), {'Access-Control-Allow-Origin': '*'}
    @ns3.expect(config_parser)
    def post(self):
        return ZConfig.save(self), {'Access-Control-Allow-Origin': '*'}

@ns4.route('/register/<string:phone_number>/')
@ns4.param('phone_number', description='Phone Number', required=True)
class Signal_Register(Resource):
    @ns4.expect(signal_activation)
    def post(self, phone_number):
        return Signaling.register(self, phone_number), {'Access-Control-Allow-Origin': '*'}

@ns4.route('/register/<string:phone_number>/activate/<string:code>/')
@ns4.param('phone_number', description='Phone Number', required=True)
@ns4.param('code', description='Activation Code', required=True)
class Signal_Register_Activation(Resource):
    def post(self, phone_number, code):
        return Signaling.activate(self, phone_number, code), {'Access-Control-Allow-Origin': '*'}

@ns4.route('/send/')
class Signal_Sender(Resource):
    @ns4.expect(signal_message)
    def post(self):
        return Signaling.send(self), {'Access-Control-Allow-Origin': '*'}

### Main app!!!
if __name__ == '__main__':
    app.run(host='0.0.0.0', port = PUBLISHED_PORT)

#############################################
# EoF    
