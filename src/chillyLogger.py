# !/usr/bin/env python
# -*- coding:utf-8 -*-

# Import Modules
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# Import Class
from src.cfgReader import get_configuration

# Define global REPO_PATH
REPO_PATH = str((Path(sys.argv[0]).parents[1]).resolve())

# Define Globals objects
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = "chilly.log"

def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    read_successful, log_cfg = get_configuration("log")
    logger = logging.getLogger(logger_name)
    # Logging levels https://docs.python.org/3/library/logging.html#levels
    logger.setLevel(int(log_cfg['level']))
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    logger.propagate = False
    return logger
