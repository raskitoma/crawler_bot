#############################################
# Plazabot - pb_crawler.py
# (c)2021, Doubtfull Productions
#--------------------------------------------
# Site crawler
#-------------------------------------------- 
# TODO  This script should round alongisde the API
#-------------------------------------------- 

# Include libraries for functionality
#import os, sys
import logging
import time
from pb_config import WAIT_TRY, WAIT_BETWEEN, LOG_URI, DEFAULT_URL, reload_config
from pb_utl import stock_check, notifier, log_store, requests, str_to_bool
from pb_string import *

# Setting log to display status
logging.getLogger().setLevel(logging.INFO)

if __name__ == '__main__':

    # Variables para uso del bot
    found_something = False # No ha encontrado nada
    bot_run = 0 # Cantidad de corridas
    bot_found = 0 # Cantidad de items encontrados 

    # Correra por siempre hasta matar el script...
    while True:
        reload_config()
        bot_run += 1 # incrementa corrida

        logging.info('***** Iteration #{}'.format(bot_run))
        text_msg = 'Starting Iteration #{}'.format(bot_run)
        log_payload = {
            'log_description' : text_msg,
            'log_type'        : LOG_ALERT,
            'log_module'      : MODULE_CRAWLER,
            'data'            : text_msg
        }
        log_store(LOG_URI, log_payload)

        f_run = open('crawler_run.lock', 'w+')
        f_run.write(str(bot_run))
        f_run.close()

        # abriendo el archivo de configuracion, leyendo lineas y cantidad de las mismas
        # TODO replace this with DB access
        file = open('z_items.cfg', 'r')
        lines = file.readlines()
        size = len(lines)
        line_num = 0

        # por cada linea en el archivo de configuracion
        for line in lines:
            line_num += 1 # conteo de lineas
            f_lin = open('crawler_lin.lock', 'w+')
            f_lin.write(str(line_num))
            f_lin.close()
            response = requests.get(DEFAULT_URL + 'Maintenance/Skip/{}/'.format(line_num))
            line_skip = str_to_bool(response.text.rstrip('\r\n'))
            if (line_skip):
                text_msg = 'Corrida {}, linea {} skipped by skipper!!'.format(bot_run, line_num)
                log_payload = {
                    'log_description' : text_msg,
                    'log_type'        : LOG_ALERT,
                    'log_module'      : MODULE_CRAWLER,
                    'data'            : text_msg
                }
                log_store(LOG_URI, log_payload)
                logging.info(text_msg)
                response = requests.post(DEFAULT_URL + 'Maintenance/Skip/{}/delete/'.format(line_num))
                continue
            if (line.find('#')==0): #comment
                text_msg = 'Corrida {}, linea {} skipped by comment!!'.format(bot_run, line_num)
                log_payload = {
                    'log_description' : text_msg,
                    'log_type'        : LOG_ALERT,
                    'log_module'      : MODULE_CRAWLER,
                    'data'            : text_msg
                }
                log_store(LOG_URI, log_payload)
                logging.info(text_msg)
                continue
            data = line.rstrip('\r\n').split(',') # remueve cr lf y split de linea en , para obtener un array (list porque python no implementa arrays)
            logging.info('Run {} - Item {} of {} *** Checking item:{}, url:{}'.format(bot_run, line_num, size, data[0], data[1]))
            log_payload = {
                'log_description' : 'Run {} - Item {} of {}'.format(bot_run, line_num, size),
                'log_type'        : LOG_EVENT,
                'log_module'      : MODULE_CRAWLER,
                'data'            : 'Run {} - Item {} of {}\nChecking item:{}\nurl on file{}'.format(bot_run, line_num, size, data[0], data[1])
            }
            log_store(LOG_URI, log_payload)
            bot_result = stock_check(data) # Ejecuta la funcion que verifica si existe o no el item (regresa True o False)
            if (bot_result): # Si existe, notificamos
                notify_text = 'Disponible {} en {}!'.format(data[0], data[1])
                notifier(notify_text)
                found_something = True # cambia variable para hacer magia mas tarde
                log_payload = {
                    'log_description' : 'FOUND Run {} - Item {} of {}'.format(bot_run, line_num, size),
                    'log_type'        : LOG_SUCCESS,
                    'log_module'      : MODULE_CRAWLER,
                    'data'            : 'Found in run {} - Item {} of {}\nYtem:{}\nurl on file{}'.format(bot_run, line_num, size, data[0], data[1])
                }
                log_store(LOG_URI, log_payload)
                # Creando skip de item
                response = requests.post(DEFAULT_URL + 'Maintenance/Skip/{}/'.format(line_num))
                bot_found += 1 # incrementa los items encontrados
            logging.info('Sanity sleep...')
            time.sleep(WAIT_BETWEEN) # pausa entre busquedas por linea en la lista de configuracion

        if (found_something): # si encontro algo al recorrer TODA la lista...
            text_msg = 'Corrida {}, se encontraron {} items!!'.format(bot_run, bot_found)
            log_payload = {
                'log_description' : text_msg,
                'log_type'        : LOG_ALERT,
                'log_module'      : MODULE_CRAWLER,
                'data'            : text_msg
            }
            log_store(LOG_URI, log_payload)
            logging.info(text_msg)
            found_something = False
            bot_found = 0
        else: # si no encuentra nada, tras  WAIT_TRY segundos reinicia la busqueda, no es necesario resetear las variables de cantidad y encontrado
            text_msg = 'Lista recorrida sin éxito... esperando {} segundos...'.format(WAIT_TRY)
            logging.info(text_msg)
            log_payload = {
                'log_description' : text_msg,
                'log_type'        : LOG_WARNING,
                'log_module'      : MODULE_CRAWLER,
                'data'            : text_msg
            }
            log_store(LOG_URI, log_payload)

            time.sleep(WAIT_TRY)
        
        logging.info('\n\nVamos otra vez...\n\n')

            
#############################################
# EoF