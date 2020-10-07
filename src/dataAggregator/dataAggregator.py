# !/usr/bin/env python
# -*- coding:utf-8 -*-

# imports Tp-Link plugin
try:
    from dataAggregator.customerTpLink import pluginTpLink
except:
    print("Tp-Link plugin not available")


class DataAggregator:
    def __init__(self, search_alias, customer):
        self.customer = customer
        if self.customer == 'TpLink':
            pluginTpLink.init_dev_by_alias(search_alias)
        else:
            print("No valid customer plugin selected")

    def get_dev_value(self):
        value = 0
        if self.customer == 'TpLink':
            value = pluginTpLink.get_dev_value()
        return value

    def get_device_valid(self):
        device_valid = False
        if self.customer == 'TpLink':
            device_valid = pluginTpLink.get_device_valid()
        return device_valid

    def get_device_ip(self):
        ip_address = ''
        if self.customer == 'TpLink':
            ip_address = pluginTpLink.get_device_ip()
        return ip_address
