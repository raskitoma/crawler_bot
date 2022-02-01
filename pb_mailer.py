#############################################
# Plazabot - pb_smtpmailer.py
# (c)2021, Doubtfull Productions
#--------------------------------------------
# Smtp mailer
#-------------------------------------------- 
# TODO This actually is a general smtp mail sender
#-------------------------------------------- 

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def create_message(sender, to, subject, message_text):
    message = MIMEMultipart()
    message['from'] = sender
    message['to'] = to
    message['subject'] = subject
    message.attach(MIMEText(message_text, 'plain'))
    return message.as_string()

def server_login(smtp_address, user_auth, pass_auth):
    server = None
    try:
        server = smtplib.SMTP(smtp_address)
        print('Connection successfull!')
    except Exception as error:
        print('Connection error: {}'.format(error))
        return None
    
    try:
        server.starttls()
    except Exception as error:
        print('SSL protocol error! ({})'.format(error))
        return None

    try:
        server.login(user_auth, pass_auth)
    except Exception as error:
        print('Auth error!({})'.format(error))
        return None
    return server

def send_mail(sender, to, subject, body, smtp_server, from_pass):
    message = create_message(sender, to, subject, body)

    server = server_login(smtp_server, sender, from_pass)

    if (server!=None):
        server.sendmail(sender, to, message)
        server.quit()
        return 'Mail sent successfully', 200
    else:
        print('Error connecting to server')
        return 'Mail error', 404

#############################################
# EoF