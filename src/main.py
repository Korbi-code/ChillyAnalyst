# !/usr/bin/env python
# -*- coding:utf-8 -*-

from dataAggregator.dataAggregator import DataAggregator
import configHandler
import telegramBot
from datetime import datetime
import threading
import time

data_aggregator = 0
detection_state = 'IDLE'
state_machine_parameter = 0
debounce_timer = 0
sleep_time = 25
TelegramHandler_object = 0

def fetch_telegrambot():
    global TelegramHandler_object
    read_successful, telegram_cfg = configHandler.get_configuration("telegram")
    if read_successful:
        # Create telegram handler object
        TelegramHandler_object = telegramBot.TelegramHandler(telegram_cfg['token'])
        while 1:
            TelegramHandler_object.start_listening()
            time.sleep(10)
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print("Process Telegram Current Time =", current_time)
    else:
        print("Invalid configuration")


def init():
    global data_aggregator
    read_successful, data_aggregator_cfg = configHandler.get_configuration("data_aggregator")

    if read_successful:
        search_alias = data_aggregator_cfg['device_name']
        customer = data_aggregator_cfg['use_plugin']
        data_aggregator = DataAggregator(search_alias, customer)
        if data_aggregator.get_device_valid:
            print("Device detected with IP:" + str(data_aggregator.get_device_ip()))
            return True
        else:
            return False
    else:
        return False


def state_machine():
    # Globals
    global detection_state
    global debounce_timer
    global state_machine_parameter
    global sleep_time
    global TelegramHandler_object

    while 1:
        # Get new value
        read_power_mw = data_aggregator.get_dev_value()
        print(read_power_mw,detection_state)

        # State Machine
        if detection_state == 'IDLE':
            if read_power_mw > int(state_machine_parameter['param_power_lower_level']):
                sleep_time = int(state_machine_parameter['param_measure_tick_rate'])
                start_time = datetime.now().strftime("%H:%M:%S")
                detection_state = 'MEASURE'
                TelegramHandler_object.send_message("Start Detected")
                #value_container.append(read_power_mw)

        elif detection_state == 'MEASURE':
            sleep_time = int(state_machine_parameter['param_measure_tick_rate'])
            if read_power_mw <= int(state_machine_parameter['param_power_debounce_level']):
                if debounce_timer < int(state_machine_parameter['param_debounce_tick_limit']):
                    debounce_timer = debounce_timer + 1
                else:
                    detection_state = 'END'
            else:
                debounce_timer = 0
            #value_container.append(read_power_mw)

        elif detection_state == 'END':
            '''
            value_container.append(read_power_mw)
            plt.plot(value_container)
            plt.ylabel('power [mw]')
            plt.xlabel('ticks [500ms]')
            plt.savefig(PGN_NAME)
            value_container.clear()
            '''
            sleep_time = int(state_machine_parameter['param_idle_tick_rate'])
            detection_state = 'IDLE'
            TelegramHandler_object.send_message("End Detected")
        else:
            # not expected to reach this state, if so .... not good
            print('invalid state')

        time.sleep(sleep_time)


def main():
    global data_aggregator
    global detection_state
    global state_machine_parameter
    read_successful,state_machine_parameter = configHandler.get_configuration("parameter")



if __name__ == '__main__':
    print("Start Main-Programm")
    init()
    main()

    thread1 = threading.Thread(target=fetch_telegrambot)
    thread1.start()

    thread2 = threading.Thread(target=state_machine)
    thread2.start()

    print("Ende Main-Programm")
