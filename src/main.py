# !/usr/bin/env python
# -*- coding:utf-8 -*-

# Import Modules
import threading
import time
import configparser
from pathlib import Path
import sys
import os
import collections
import datetime

# Import Module
sys.path.append(os.getcwd())
from src.dataAggregator.dataAggregator import DataAggregator
from src.telegramBot import TelegramHandler
from src.dataContainer import DataContainer
from src.cfgReader import get_configuration
from src.chillyLogger import *

# Define global REPO_PATH
REPO_PATH = str((Path(sys.argv[0]).parents[1]).resolve())

# Define Globals objects
DataAggregator_object = 0
TelegramHandler_object = False
DataContainer_object = 0
InputFilter_deque = 0
_LOGGER = get_logger(__file__)

# State machine params
PARAMS = configparser.ConfigParser()
configFilePath = REPO_PATH + r'/config/config.cfg'
PARAMS.read(configFilePath)
PARAM_POWER_LOWER_LEVEL = int(PARAMS.get('parameter', 'PARAM_POWER_LOWER_LEVEL'))
PARAM_POWER_DEBOUNCE_LEVEL = int(PARAMS.get('parameter', 'PARAM_POWER_DEBOUNCE_LEVEL'))
PARAM_EMETER_PLUG_RESOLUTION = float(PARAMS.get('parameter', 'PARAM_EMETER_PLUG_RESOLUTION'))
PARAM_IDLE_TICK_RATE = int(PARAMS.get('parameter', 'PARAM_IDLE_TICK_RATE'))
PARAM_MEASURE_TICK_RATE = int(PARAMS.get('parameter', 'PARAM_MEASURE_TICK_RATE'))
PARAM_DEBOUNCE_TICK_LIMIT = int(PARAMS.get('parameter', 'PARAM_DEBOUNCE_TICK_LIMIT'))
CONNECTION_LOST_TIMER_IN_MIN = int(PARAMS.get('parameter', 'CONNECTION_LOST_TIMER_IN_MIN'))


def init():
    Path(REPO_PATH + r'/data/').mkdir(parents=True, exist_ok=True)

    global DataAggregator_object
    DataAggregator_object = DataAggregator()

    global DataContainer_object
    DataContainer_object = DataContainer()

    global InputFilter_deque
    read_successful, cfg_parameter = get_configuration("parameter")
    InputFilter_deque = collections.deque(maxlen=int(cfg_parameter["filter_queue"]))
    InputFilter_deque.append(0)


def cyclic_telegram_handler():
    global TelegramHandler_object
    read_successful, cfg_token = get_configuration("telegram")
    if read_successful:
        TelegramHandler_object = TelegramHandler(cfg_token["token"])
        TelegramHandler_object.start()
        _LOGGER.info("Telegram Handler Startet")
    else:
        _LOGGER.error("Telegram access token not found in config")


def cyclic_state_machine_handler():
    global TelegramHandler_object
    global InputFilter_deque

    last_valid_timestamp = datetime.datetime.now()

    while 1:
        if DataAggregator_object.get_device_valid():
            last_valid_timestamp = datetime.datetime.now()

            # Get new value
            read_power_mw, read_power_mw_valid = DataAggregator_object.get_dev_value()
            read_power_mw = round(float(read_power_mw * PARAM_EMETER_PLUG_RESOLUTION), 1)

            if not read_power_mw_valid:
                TelegramHandler_object.send_message("Device returns invalid value", level='Expert')

            InputFilter_deque.append(read_power_mw)
            read_power_mw_mean = round(sum(InputFilter_deque) / len(InputFilter_deque), 1)
            DataContainer_object.add_new_value(read_power_mw_mean)
            _LOGGER.debug("READ_POWER: " + str(read_power_mw) + " MEAN:" + str(read_power_mw_mean))

            if TelegramHandler_object.graph_requested():
                if DataContainer_object.create_graph():
                    TelegramHandler_object.send_html(DataContainer_object.get_html())

            # State Machine
            if cyclic_state_machine_handler.detection_state == 'IDLE':
                if read_power_mw_mean > PARAM_POWER_LOWER_LEVEL:
                    cyclic_state_machine_handler.sleep_time = PARAM_MEASURE_TICK_RATE
                    DataContainer_object.enable_acquisition()
                    cyclic_state_machine_handler.detection_state = 'MEASURE'
                    TelegramHandler_object.send_message("Start Detected")
                    # TelegramHandler_object.send_user_question()
                    cyclic_state_machine_handler.debounce_timer = 0
                    _LOGGER.info("Start Detected - State Transition to MEASURE")

            elif cyclic_state_machine_handler.detection_state == 'MEASURE':
                if read_power_mw_mean <= PARAM_POWER_DEBOUNCE_LEVEL:
                    if cyclic_state_machine_handler.debounce_timer < PARAM_DEBOUNCE_TICK_LIMIT:
                        cyclic_state_machine_handler.debounce_timer += 1
                        _LOGGER.debug("Debouncing")
                    else:
                        DataContainer_object.disable_acquisition()
                        cyclic_state_machine_handler.detection_state = 'END'
                        _LOGGER.debug("State Transition to END")
                else:
                    cyclic_state_machine_handler.debounce_timer = 0

            elif cyclic_state_machine_handler.detection_state == 'END':
                cyclic_state_machine_handler.sleep_time = PARAM_IDLE_TICK_RATE
                cyclic_state_machine_handler.detection_state = 'IDLE'
                TelegramHandler_object.send_message("End Detected")
                _LOGGER.info("End Detected")
            else:
                # not expected to reach this state, if so .... not good
                _LOGGER.error("Invalid State")

        else:
            _LOGGER.info("Searching new device")
            try:
                TelegramHandler_object.send_message("Keine Verbindung zur Steckdose! Ich suche!", level='Expert')
            except:
                pass

            _LOGGER.debug("Connection lost in min: " +str(((datetime.datetime.now() - last_valid_timestamp).total_seconds()) / 60))

            if ((datetime.datetime.now() - last_valid_timestamp).total_seconds()) / 60 >= CONNECTION_LOST_TIMER_IN_MIN:
                cyclic_state_machine_handler.sleep_time = PARAM_IDLE_TICK_RATE
                cyclic_state_machine_handler.detection_state = 'IDLE'
                DataContainer_object.disable_acquisition()
                _LOGGER.info("Connection lost time reached")

            DataAggregator_object.init_dev()

        time.sleep(cyclic_state_machine_handler.sleep_time)


# initialize statics for state_machine
cyclic_state_machine_handler.detection_state = 'IDLE'
cyclic_state_machine_handler.sleep_time = PARAM_IDLE_TICK_RATE

if __name__ == '__main__':
    init()

    thread1 = threading.Thread(target=cyclic_telegram_handler)
    thread1.start()

    thread2 = threading.Thread(target=cyclic_state_machine_handler)
    thread2.start()
