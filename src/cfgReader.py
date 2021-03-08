# !/usr/bin/env python
# -*- coding:utf-8 -*-

from configparser import ConfigParser
import pathlib

# Define global REPO_PATH
REPO_BASE_FOLDER = pathlib.Path(__file__).parent.absolute().parents[0]
PATH_TO_CONFIG_FILE = REPO_BASE_FOLDER.joinpath('config/config.cfg')

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

