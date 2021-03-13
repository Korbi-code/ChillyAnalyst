# !/usr/bin/env python
# -*- coding:utf-8 -*-

# imports
import configparser

# Import Module
from src.chillyLogger import *

# Globals
_LOGGER = get_logger(__file__)

# imports Tp-Link plugin
try:
    from src.dataAggregator.customerTpLink import pluginTpLink
except:
    _LOGGER.warning("Tp-Link plugin not available")

# imports Tasmota plugin
try:
    from src.dataAggregator.customerTasmota import pluginTasmota
except:
    _LOGGER.warning("Tasmota plugin not available")


# Define global REPO_PATH
REPO_PATH = str((Path(sys.argv[0]).parents[1]).resolve())

# config handler
DATAAGGREGATOR_CFG = configparser.ConfigParser()
configFilePath = REPO_PATH+r'/config/config.cfg'
DATAAGGREGATOR_CFG.read(configFilePath)


class DataAggregator:
    def __init__(self):
        self.customer = DATAAGGREGATOR_CFG.get('data_aggregator', 'use_plugin')
        self.search_alias = DATAAGGREGATOR_CFG.get('data_aggregator', 'device_name')

    def init_dev(self):
        if self.customer == 'TpLink':
            pluginTpLink.init_dev_by_alias(self.search_alias)
        elif self.customer == 'Tasmota':
            pluginTasmota.init_dev_by_alias(self.search_alias)
        else:
            print("No valid customer plugin selected")

    def get_dev_value(self):
        value = 0
        value_valid = False
        if self.customer == 'TpLink':
            value, value_valid = pluginTpLink.get_dev_value()
        elif self.customer == 'Tasmota':
            value, value_valid = pluginTasmota.get_dev_value()
        return value, value_valid

    def get_device_valid(self):
        device_valid = False
        if self.customer == 'TpLink':
            device_valid = pluginTpLink.get_device_valid()
        elif self.customer == 'Tasmota':
            device_valid = pluginTasmota.get_device_valid()
        return device_valid

    def get_device_ip(self):
        ip_address = ''
        if self.customer == 'TpLink':
            ip_address = pluginTpLink.get_device_ip()
        elif self.customer == 'Tasmota':
            ip_address = pluginTasmota.get_device_ip()
        return ip_address
