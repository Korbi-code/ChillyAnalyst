# !/usr/bin/env python
# -*- coding:utf-8 -*-

# imports
import requests
import socket
from queue import Queue
from threading import Thread

# Import Module
from src.chillyLogger import *

# Globals
_LOGGER = get_logger(__file__)
detected_device = False
detected_device_ip = False
detected_device_is_valid = False
deviceName = False
raw_power_timeout_safe = 0
power = 0
valid_ips = []
connection_timeout_debounce = 0

# TODO why?
testIP = "8.8.8.8"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((testIP, 0))
ipaddr = s.getsockname()[0]
host = socket.gethostname()
myIP = socket.gethostbyname(socket.gethostname())
myIP = ipaddr
ips = myIP.split('.')


def init_dev_by_alias(search_alias):
    """
    Init Device by alias
    :param search_alias:
    :return:
    """
    global detected_device
    global detected_device_ip
    global detected_device_is_valid
    '''
    Search based on the configured alias the device in network.
    Create link between search_alias and plug IP address to access the values
    :return: IP address to plug
    '''
    logging.basicConfig(level=logging.INFO)
    ip_to_return = scanner(search_alias)
    if ip_to_return:
        detected_device_ip = ip_to_return
        detected_device_is_valid = True


def get_dev_value():
    """
    :return: returns the actual e-meter value
    """
    # Globals
    global detected_device
    global detected_device_ip
    global detected_device_is_valid
    valid = False

    if detected_device_is_valid:
        value, valid = read_value_from_device_ip(detected_device_ip)
    else:
        value = 0
    return value, valid


def get_device_valid():
    """
    false device is not usable
    True device is ready to read the e-meter values
    """
    return detected_device_is_valid


def get_device_ip():
    """
    :return: the device IP address
    """
    return detected_device_ip


def find_device_by_ip(q):
    global power
    while True:
        if q.empty():
            # print("queue empty")
            break
        check_ip = q.get()  # Take element out of q
        ''' http://192.168.0.136/cm?cmnd=DeviceName finds the name set in Tasmota'''
        status_url = 'http://' + (
                '%s.%s.%s.%s' % (str(ips[0]), str(ips[1]), str(ips[2]), str(check_ip))) + '/cm?cmnd=Status%208'
        # print(status_url)
        try:
            r = requests.get(url=status_url, timeout=0.3)
            try:
                json_con = r.json()
                # print(json_con)
                if str(json_con).find(
                        'ENERGY') != -1:  # todo find better filter methode for Tasmota devices (first check devive name and the for energy)
                    power = str(json_con["StatusSNS"]["ENERGY"]["Power"])
                    # print("Power: " + power)
                    valid_ips.append(check_ip)
            except ValueError:
                # print("no json")
                pass
        except (
                requests.ConnectTimeout, requests.HTTPError, requests.ReadTimeout, requests.Timeout,
                requests.ConnectionError):
            # print("no device")
            pass
        q.task_done()


# todo create device object?
def scanner(search_alias):
    global deviceName
    deviceName = search_alias
    print("My IP is: " + myIP)
    '''
    put here all Ips addresses into q with .put(arg)
    '''
    q = Queue(maxsize=256)
    for x in range(255):
        q.put(x)

    '''
    Start num_threads and assign each thread the do_stuff function
    All of them take the same q element as input
    '''
    num_threads = 25
    for i in range(num_threads):
        worker = Thread(target=find_device_by_ip, args=(q,))
        worker.setDaemon(True)
        worker.start()

    q.join()  # Waits until q is empty

    if len(valid_ips) > 0:
        foundIP = '%s.%s.%s.%s' % (ips[0], ips[1], ips[2], valid_ips[0])
        _LOGGER.info('finished search, found this device:' + str(foundIP))
        return foundIP
    else:
        _LOGGER.info('finished search, no devices found :(')
        return False


def read_value_from_device_ip(device_ip):
    global detected_device_is_valid
    global detected_device_ip
    global connection_timeout_debounce
    global raw_power_timeout_safe

    local_power = 0
    status_url = 'http://' + str(device_ip) + '/cm?cmnd=Status%208'

    local_power_valid = False
    try:
        r = requests.get(url=status_url, timeout=0.6,verify=False)
        try:
            json_con = r.json()
            if str(json_con).find('ENERGY') != -1:
                local_power = str(json_con["StatusSNS"]["ENERGY"]["Power"])
                local_power_valid = True
                connection_timeout_debounce = 0
                _LOGGER.debug("RAW Power:" + str(local_power))
        except ValueError as e:
            _LOGGER.info(e)
            local_power = 0
            connection_timeout_debounce += 1
            pass
    except (
            requests.ConnectTimeout, requests.HTTPError, requests.ReadTimeout, requests.Timeout,
            requests.ConnectionError) as e:
        _LOGGER.info(e)
        connection_timeout_debounce += 1
        local_power = 0
        pass

    if connection_timeout_debounce > 5:
        detected_device_is_valid = False
        detected_device_ip = False
        raw_power_timeout_safe = 0
        valid_ips.clear()

    if local_power_valid:
        raw_power_timeout_safe = int(local_power)



    return int(raw_power_timeout_safe), local_power_valid
