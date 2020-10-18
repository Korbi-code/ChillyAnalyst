# !/usr/bin/env python
# -*- coding:utf-8 -*-

# imports
import asyncio
import logging
from src.dataAggregator.customerTasmota.scanner import scanner
from src.dataAggregator.customerTasmota.scanner import power
from src.dataAggregator.customerTasmota.scanner import update

_LOGGER = logging.getLogger(__name__)
detected_device = False
detected_device_ip = False
detected_device_is_valid = False


def init_dev_by_alias(search_alias):
    '''
    Init Device by alias
    :param search_alias:
    :return:
    '''
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

    # TODO: is it necessary?
    '''
    create the object_device based on the detected ip
    object provides the access to the plug
    '''
    # detected_device = SmartDevice(detected_device_ip)


def get_dev_value():
    """
    :return: returns the actual e-meter value
    """
    # Globals
    global detected_device
    global detected_device_ip
    global detected_device_is_valid

    # Get and return value of plug
    if detected_device_is_valid:
        asyncio.run(update(detected_device_ip))
        value = power
    else:
        value = 0
    return value


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
