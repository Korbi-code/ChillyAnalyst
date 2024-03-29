# !/usr/bin/env python
# -*- coding:utf-8 -*-

# imports
import asyncio
import logging
from kasa import Discover
from kasa import SmartDevice
from src.chillyLogger import get_logger

# Globals
_LOGGER = get_logger(__file__)
detected_device = False
detected_device_ip = False
detected_device_is_valid = False


def init_dev_by_alias(search_alias):
    global detected_device
    global detected_device_ip
    global detected_device_is_valid
    """
    Search based on the configured alias the device in network.
    Create link between search_alias and plug IP address to access the values
    :return: IP address to plug
    """
    ip_to_return = False
    logging.basicConfig(level=logging.INFO)

    devices = asyncio.run(Discover.discover())
    for ip, dev in devices.items():
        if dev.alias == search_alias:
            ip_to_return = ip
    detected_device_ip = ip_to_return
    _LOGGER.info("detected device IP: "+str(detected_device_ip))

    """
    create the object_device based on the detected ip
    object provides the access to the plug
    """
    detected_device = SmartDevice(detected_device_ip)
    asyncio.run(detected_device.update())
    if detected_device.has_emeter:
        detected_device_is_valid = True


def get_dev_value():
    """
    :return: returns the actual emeter value
    """
    # Globals
    global detected_device
    global detected_device_ip
    global detected_device_is_valid

    # Get and return value of plug
    if detected_device_is_valid:
        asyncio.run(detected_device.update())
        value = detected_device.emeter_realtime['power_mw']
    else:
        value = 0
    return value, True


def get_device_valid():
    """
    false device is not usable
    True device is ready to read the emeter values
    """
    return detected_device_is_valid


def get_device_ip():
    """
    :return: the device IP address
    """
    return detected_device_ip
