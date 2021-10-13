#!/usr/bin/env python
# -*- coding: utf-8 -*-


from tinydb import TinyDB, Query
from pathlib import Path
from src.chillyLogger import *
import os

from cfgReader import *

_LOGGER = get_logger(__file__)


def get_is_user_registered(id) -> bool:
    read_successful, cfg_path = get_configuration("telegram")
    path = REPO_PATH + os.path.join(cfg_path["subscribed_users_path"])

    try:
        db = TinyDB(path + '/' + cfg_path["subscribed_users_filename"])
        db_field = Query()
        db.search(db_field.type == id)

        detected = False
        for item in db:
            if id == item['id']:
                detected = True
        return detected

    except:
        _LOGGER.info("No users registered")
        return False


def get_all_active_users():
    read_successful, cfg_path = get_configuration("telegram")
    path = REPO_PATH + os.path.join(cfg_path["subscribed_users_path"])

    try:
        db = TinyDB(path + '/' + cfg_path["subscribed_users_filename"])
        db_field = Query()
        db.search(db_field.type == 'id')
        return db

    except:
        _LOGGER.info("No users registered")
        return False


def register_new_user(id, firstname, lastname):
    read_successful, cfg_path = get_configuration("telegram")
    path = REPO_PATH + os.path.join(cfg_path["subscribed_users_path"])

    try:
        if not os.path.exists(path):
            os.makedirs(path)

        db = TinyDB(path + '/' + cfg_path["subscribed_users_filename"])

        item = {'id': id, 'firstname': firstname, 'lastname': lastname, 'type': 'basic', 'notification': 'True'}
        _LOGGER.debug("register_new_user" + str(item))
        db.insert(item)
        return True

    except:
        return False


def update_user_entry(id, field, value) -> bool:
    read_successful, cfg_path = get_configuration("telegram")
    path = REPO_PATH + os.path.join(cfg_path["subscribed_users_path"])

    try:
        db = TinyDB(path + '/' + cfg_path["subscribed_users_filename"])
        db_field = Query()
        db.search(db_field.id == id)
        db.update({field: value})
        return True

    except:
        _LOGGER.info("No users registered")
        return False
