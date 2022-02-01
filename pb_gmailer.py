#############################################
# Plazabot - pb_gmailer.py
# (c)2021, Doubtfull Productions
#--------------------------------------------
# Gmail lib file
# Mailer GMAIL
# Activar acceso en  https://developers.google.com/gmail/api/quickstart/python 
# descargar credentials.json y grabar en folder de bot
# primera corrida solicita acceso al oauth de gmail para generar un token
# Esta biblioteca no corre en docker debido al proceso interactivo
# que es requerido la primera vez y cada que el token expira
#-------------------------------------------- 
# TODO
#-------------------------------------------- 

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
from apiclient import errors
from email.mime.text import MIMEText
from google.oauth2 import service_account

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SERVICE_ACCOUNT_FILE = 'credentials.json'

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject
    message['from'] = sender
    return { 'raw' : base64.urlsafe_b64encode(message.as_string().encode()).decode() }
    
def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        return message
    except errors.HttpError as error:
        print ('Error: {}'.format(error))

def service_account_login(email_from):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:        
            credentials = InstalledAppFlow.from_client_secrets_file(SERVICE_ACCOUNT_FILE, SCOPES)
            creds = credentials.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
    return service

def send_gmail(email_from, email_to, email_subject, email_content):
    service = service_account_login(email_from)
    message = create_message(email_from, email_to, email_subject, email_content)
    sent = send_message(service, 'me', message)
    return sent

#############################################
# EoF