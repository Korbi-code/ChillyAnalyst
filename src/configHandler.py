# !/usr/bin/env python
# -*- coding:utf-8 -*-
from configparser import ConfigParser

PATH_TO_CONFIG_FILE = '../config/config.cfg'

def get_configuration(section):
    conf_parser = ConfigParser()
    conf_parser.read(PATH_TO_CONFIG_FILE)
    dict_configuration = {}
    if conf_parser.has_section(section):
        for element in conf_parser.items(section):
            dict_configuration[element[0]] = element[1]
    if len(dict_configuration) != 0:
        return True, dict_configuration
    else:
        return False, dict_configuration

def main():
    print(get_configuration("telegram"))
    print(get_configuration("data_aggregator"))
    print(get_configuration("paths"))
    print(get_configuration("parameter"))

if __name__ == '__main__':
    main()
