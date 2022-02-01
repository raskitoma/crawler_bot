#############################################
# Plazabot - pb_clickatelly.py
# (c)2021, Doubtfull Productions
#--------------------------------------------
# Custom Clickatell library
#-------------------------------------------- 
# TODO
#-------------------------------------------- 
from flask import config
import requests
import json
from pb_config import CLICKATELL_URI, CLICKATELL_AUTH, CLICKATELL_CHAN, reload_config

def payloader(pay_channel, pay_to, pay_msg):
    new_payload = {
        'messages' : [
            {
                'channel' : CLICKATELL_CHAN[pay_channel],
                'to'      : pay_to,
                'content' : pay_msg
            }
        ]
    }
    return json.dumps(new_payload)
   
def poster(payload):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': CLICKATELL_AUTH,
    }

    response = requests.post(CLICKATELL_URI, headers=headers, data=payload)

    return response

def send_sms(target_no, target_msg):
    reload_config()
    payload = payloader(0, target_no, target_msg)
    return poster(payload)

def send_whatsapp(target_no, target_msg):
    reload_config()
    payload = payloader(1, target_no, target_msg)
    return poster(payload)

#############################################
# EoF