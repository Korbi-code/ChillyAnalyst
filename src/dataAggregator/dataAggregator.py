# !/usr/bin/env python
# -*- coding:utf-8 -*-

# import module
import configparser

import sys
sys.path.append('../')
# imports Tp-Link plugin
try:
    from dataAggregator.customerTpLink import pluginTpLink
except:
    print("Tp-Link plugin not available")

# imports Tasmota plugin
try:
    from dataAggregator.customerTasmota import pluginTasmota
except:
    print("Tasmota plugin not available")

# config handler
DATAAGGREGATOR_CFG = configparser.ConfigParser()
configFilePath = r'../config/config.cfg'
DATAAGGREGATOR_CFG.read(configFilePath)


class DataAggregator:
    def __init__(self):
        self.customer = DATAAGGREGATOR_CFG.get('data_aggregator', 'use_plugin')
        self.search_alias = DATAAGGREGATOR_CFG.get('data_aggregator', 'device_name')
        if self.customer == 'TpLink':
            pluginTpLink.init_dev_by_alias(self.search_alias)
        elif self.customer == 'Tasmota':
            pluginTasmota.init_dev_by_alias(self.search_alias)
        else:
            print("No valid customer plugin selected")

    def get_dev_value(self):
        value = 0
        if self.customer == 'TpLink':
            value = pluginTpLink.get_dev_value()
        elif self.customer == 'Tasmota':
            value = pluginTasmota.get_dev_value()
        return value

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
