# !/usr/bin/env python
# -*- coding:utf-8 -*-

# Import Modules
import threading
import time
from datetime import datetime
import configparser
from pathlib import Path

# Import Class
from dataAggregator.dataAggregator import DataAggregator
from telegramBot import TelegramHandler
from dataContainer import DataContainer

# Define Globals objects
DataAggregator_object = 0
TelegramHandler_object = False
DataContainer_object = 0

# State machine params
PARAMS = configparser.ConfigParser()
configFilePath = r'../config/config.cfg'
PARAMS.read(configFilePath)
PARAM_POWER_LOWER_LEVEL = int(PARAMS.get('parameter', 'PARAM_POWER_LOWER_LEVEL'))
PARAM_POWER_DEBOUNCE_LEVEL = int(PARAMS.get('parameter', 'PARAM_POWER_DEBOUNCE_LEVEL'))
PARAM_EMETER_PLUG_RESOLUTION = float(PARAMS.get('parameter', 'PARAM_EMETER_PLUG_RESOLUTION'))
PARAM_IDLE_TICK_RATE = int(PARAMS.get('parameter', 'PARAM_IDLE_TICK_RATE'))
PARAM_MEASURE_TICK_RATE = int(PARAMS.get('parameter', 'PARAM_MEASURE_TICK_RATE'))
PARAM_DEBOUNCE_TICK_LIMIT = int(PARAMS.get('parameter', 'PARAM_DEBOUNCE_TICK_LIMIT'))


def init():
    # Create data path if not existing
    Path(r'../data/').mkdir(parents=True, exist_ok=True)

    init_data_aggregator()
    init_telegram()
    init_data_container()


def init_telegram():
    global TelegramHandler_object
    TelegramHandler_object = TelegramHandler()


def init_data_aggregator():
    global DataAggregator_object
    DataAggregator_object = DataAggregator()


def init_data_container():
    global DataContainer_object
    DataContainer_object = DataContainer()


def cyclic_telegram_handler():
    global TelegramHandler_object
    if TelegramHandler_object:
        while 1:
            TelegramHandler_object.start_listening()
            time.sleep(10)
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print("Process Telegram Current Time =", current_time)
    else:
        print('Telegram bot is Invalid - This is critical')


def cyclic_state_machine_handler():
    while 1:
        # Get new value
        read_power_mw = DataAggregator_object.get_dev_value()
        DataContainer_object.add_new_value(read_power_mw)
        # State Machine
        if cyclic_state_machine_handler.detection_state == 'IDLE':
            if read_power_mw > PARAM_POWER_LOWER_LEVEL:
                cyclic_state_machine_handler.sleep_time = PARAM_MEASURE_TICK_RATE
                DataContainer_object.enable_acquisition()
                cyclic_state_machine_handler.detection_state = 'MEASURE'
                TelegramHandler_object.send_message("Start Detected")

        elif cyclic_state_machine_handler.detection_state == 'MEASURE':
            if read_power_mw <= PARAM_POWER_DEBOUNCE_LEVEL:
                if cyclic_state_machine_handler.debounce_timer < PARAM_DEBOUNCE_TICK_LIMIT:
                    cyclic_state_machine_handler.debounce_timer += 1
                else:
                    DataContainer_object.disable_acquisition()
                    cyclic_state_machine_handler.detection_state = 'END'
            else:
                cyclic_state_machine_handler.debounce_timer = 0

        elif cyclic_state_machine_handler.detection_state == 'END':
            cyclic_state_machine_handler.sleep_time = PARAM_IDLE_TICK_RATE
            if DataContainer_object.create_graph(PARAM_EMETER_PLUG_RESOLUTION):
                TelegramHandler_object.send_png(DataContainer_object.get_png())
            cyclic_state_machine_handler.detection_state = 'IDLE'
            TelegramHandler_object.send_message("End Detected")
        else:
            # not expected to reach this state, if so .... not good
            print('invalid state')

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