#############################################
# Plazabot - pb_db.py
# (c)2021, Doubtfull Productions
#--------------------------------------------
# Master DB file
#-------------------------------------------- 
# TODO
#-------------------------------------------- 

from flask_sqlalchemy import SQLAlchemy
from pb_config import app, dump_datetime

# Creating SQLAlchemy db instance
db = SQLAlchemy(app)

class MasterSites(db.Model):
    '''
    Sites master table
    '''
    __tablename__ = 'mastersites'
    id = db.Column('id', db.String(30), primary_key = True) # Site master key id
    description = db.Column('description', db.Text, nullable = False) # Description for site
    root_url = db.Column('root_url', db.Text, nullable = False) # Root url
    object_type = db.Column('object_type', db.Text, nullable = False) # Object type used by selenium (class, id, name)
    object_name = db.Column('object_name', db.Text, nullable = False) # Name for object

    def __init__(self, id, description, root_url, object_type, object_name):
        self.id = id
        self.description = description
        self.root_url = root_url
        self.object_type = object_type
        self.object_name = object_name

    def __repr__(self):
        return f'id={self.id}, description={self.description}, root_url={self.root_url}, object_type={self.object_type}, object_name={self.object_name}'

    @property
    def serialize(self):
        '''
        Just to return object data in an easy, serializable way
        '''
        return {
            'id'         : self.id,
            'description': self.description,
            'root_url'   : self.root_url,
            'object_type': self.object_type,
            'object_name': self.object_name
        }

class Items(db.Model):
    '''
    Items table
    '''
    __tableame__ = 'items'
    id = db.Column('id', db.String(30), primary_key = True) # item id
    master = db.Column('master', db.String(30), nullable = False) # Site master key id
    description = db.Column('description', db.Text, nullable = False) # Description for id
    extra_url = db.Column('extra_url', db.Text, nullable = False) # extra url for item in current site

    def __init__(self, id, master, description, extra_url):
        self.id = id
        self.master = master
        self.description = description
        self.extra_url = extra_url

    def __repr__(self):
        return f'id={self.id}, master={self.master}, description={self.description}, extra_url={self.extra_url}'

    @property
    def serialize(self):
        '''
        Just to return object data in an easy, serializable way
        '''
        return {
            'id'         : self.id,
            'master'     : self.master,
            'description': self.description,
            'extra_url'  : self.extra_url
        }

class Skipables(db.Model):
    '''
    Skipables table
    '''
    __tablename__ = 'skipables'
    id = db.Column('id', db.Integer, primary_key = True) # skip id
    line = db.Column('line', db.Integer, nullable = False) # line 2 skip
    until = db.Column('until', db.DateTime, nullable = False) # how long 2 skip

    def __init__(self, id, line, until):
        self.id = id
        self.line = line
        self.until = until

    def __repr__(self):
        return f'id={self.id}, line={self.line}, until={dump_datetime(self.until)}'
    
    @property
    def serialize(self):
        return {
            'id'   : self.id,
            'line' : self.line,
            'until': dump_datetime(self.until)
        }


class Logs(db.Model):
    '''
    Logs table
    '''
    __tablename__ = 'logs'
    id = db.Column('id', db.Integer, primary_key = True) # Log id
    timestamp = db.Column('timestamp', db.DateTime, nullable = False) # Log time stamp
    type = db.Column('type', db.String(30), nullable = False) # Log entry type
    module = db.Column('module', db.String(30), nullable = False) # Log reporting module
    description = db.Column('description', db.Text, nullable = False) # Log description
    data = db.Column('data', db.Text) # Log related data (html etc)
    image = db.Column('image', db.Text, nullable = True) # Log related binary data (screenshot)

    def __init__(self, id, timestamp, type, module, description, data, image):
        self.id = id
        self.timestamp = timestamp
        self.type = type
        self.module = module
        self.description = description
        self.data = data
        self.image = image

    def __repr__(self):
        return f'id={self.id}, timestamp={dump_datetime(self.timestamp)}, type={self.type}, module={self.module}, \
            description={self.description}, data={self.data}, \
            image={self.image}'

    @property
    def serialize(self):
        '''
        Just to return object data in an easy, serializable way
        '''
        return {
            'id'         : self.id,
            'timestamp'  : dump_datetime(self.timestamp),
            'type'       : self.type,
            'module'     : self.module,
            'description': self.description,
            'data'       : self.data,
            'image'      : self.image
        }


# Call db creation
db.create_all()

#############################################
# EoF