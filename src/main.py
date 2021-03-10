# !/usr/bin/env python
# -*- coding:utf-8 -*-

# Import Modules
import threading
import time
import configparser
from pathlib import Path
import sys
import os

# Import Class
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


def init():
    Path(REPO_PATH + r'/data/').mkdir(parents=True, exist_ok=True)

    global DataAggregator_object
    DataAggregator_object = DataAggregator()

    global DataContainer_object
    DataContainer_object = DataContainer()


def cyclic_telegram_handler():
    global TelegramHandler_object
    read_successful, cfg_token = get_configuration("telegram")
    if read_successful:
        TelegramHandler_object = TelegramHandler(cfg_token["token"])
        TelegramHandler_object.start()
        _LOGGER.debug("Telegram Handler Startet")
    else:
        _LOGGER.error("Telegram access token not found ic config")


def cyclic_state_machine_handler():
    global TelegramHandler_object

    while 1:
        # Get new value
        read_power_mw = DataAggregator_object.get_dev_value() * PARAM_EMETER_PLUG_RESOLUTION
        DataContainer_object.add_new_value(read_power_mw)
        _LOGGER.debug(read_power_mw)

        # State Machine
        if cyclic_state_machine_handler.detection_state == 'IDLE':
            if read_power_mw > PARAM_POWER_LOWER_LEVEL:
                cyclic_state_machine_handler.sleep_time = PARAM_MEASURE_TICK_RATE
                DataContainer_object.enable_acquisition()
                cyclic_state_machine_handler.detection_state = 'MEASURE'
                TelegramHandler_object.send_message("Start Detected")
                cyclic_state_machine_handler.debounce_timer = 0
                _LOGGER.info("Start Detected - State Transition to MEASURE")

        elif cyclic_state_machine_handler.detection_state == 'MEASURE':
            if read_power_mw <= PARAM_POWER_DEBOUNCE_LEVEL:
                if cyclic_state_machine_handler.debounce_timer < PARAM_DEBOUNCE_TICK_LIMIT:
                    cyclic_state_machine_handler.debounce_timer += 1
                    _LOGGER.info("Debouncing")
                else:
                    DataContainer_object.disable_acquisition()
                    cyclic_state_machine_handler.detection_state = 'END'
                    _LOGGER.info("State Transition to END")
            else:
                cyclic_state_machine_handler.debounce_timer = 0

        elif cyclic_state_machine_handler.detection_state == 'END':
            cyclic_state_machine_handler.sleep_time = PARAM_IDLE_TICK_RATE
            if DataContainer_object.create_graph(PARAM_EMETER_PLUG_RESOLUTION):
                TelegramHandler_object.send_html(DataContainer_object.get_html())
            cyclic_state_machine_handler.detection_state = 'IDLE'
            TelegramHandler_object.send_message("End Detected")
            _LOGGER.info("End Detected")
        else:
            # not expected to reach this state, if so .... not good
            _LOGGER.error("Invalid State")

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
