# !/usr/bin/env python
# -*- coding:utf-8 -*-

# imports
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

# import kasa Lib dependencies
from kasa import Discover
from kasa import SmartDevice

detected_device = 0
detected_device_ip = 0
detected_device_is_valid = 0

def init_dev_by_alias(search_alias):
    '''
    Search based on the configured alias the device in network.
    Create link between search_alias and plug IP address to access the values
    :return: IP adress to plug
    '''
    global detected_device
    global detected_device_ip
    global detected_device_is_valid


    ip_to_return = False
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()

    async def _on_device(dev):
        await dev.update()
        _LOGGER.info("Got device: %s", dev)

    devices = loop.run_until_complete(Discover.discover(on_discovered=_on_device))
    for ip, dev in devices.items():
        print(ip)
        if dev.alias == search_alias:
            ip_to_return = ip
    detected_device_ip = ip_to_return

    '''
    create the object_device based on the detected ip
    object provides the acces to the plug
    '''
    detected_device = SmartDevice(detected_device_ip)
    asyncio.run(detected_device.update())
    if detected_device.has_emeter:
        detected_device_is_valid = True

def get_dev_value():
    '''
    :return: returns the acutal emeter value
    '''
    asyncio.run(detected_device.update())
    return detected_device.emeter_realtime

def get_device_valid(self):
    '''
    false device is not usable
    True device is ready to read the emeter values
    '''
    return True

