# !/usr/bin/env python
# -*- coding:utf-8 -*-

# imports
from paho.mqtt import client as mqtt_client
import socket

# Import Module
from src.chillyLogger import *

detected_device = False
detected_device_ip = False
detected_device_is_valid = False
_LOGGER = get_logger(__file__)
myIP = socket.gethostbyname(socket.gethostname())
print(myIP)

def init_dev_by_alias(search_alias):
    '''
    Init Device by alias
    :param search_alias:
    :return:
    '''


def get_dev_value():
    '''
    :return: returns the actual emeter value
    '''
    return value, True


def get_device_valid():
    '''
    false device is not usable
    True device is ready to read the emeter values
    '''
    return detected_device_is_valid


def get_device_ip():
    '''
    :return: the device IP address
    '''
    return detected_device_ip
