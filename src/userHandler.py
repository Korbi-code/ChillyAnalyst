#!/usr/bin/env python
# -*- coding: utf-8 -*-


from tinydb import TinyDB, Query
from src.chillyLogger import *
import os
from cfgReader import get_configuration

_LOGGER = get_logger(__file__)


def get_is_user_registered(user_id) -> bool:
    read_successful, cfg_path = get_configuration("telegram")
    path = REPO_PATH + os.path.join(cfg_path["subscribed_users_path"])

    try:
        db = TinyDB(os.sep.join([path, cfg_path["subscribed_users_filename"]]))
        db_field = Query()
        return db.contains(db_field.userId == user_id)

    except Exception as e:
        _LOGGER.info(e)
        return False


def get_all_active_users():
    read_successful, cfg_path = get_configuration("telegram")
    path = REPO_PATH + os.path.join(cfg_path["subscribed_users_path"])

    try:
        db = TinyDB(os.sep.join([path, cfg_path["subscribed_users_filename"]]))
        db_field = Query()
        db.search(db_field.type == 'id')
        return db

    except Exception as e:
        _LOGGER.info(e)
        return False


def register_new_user(user_id, firstname, lastname):
    read_successful, cfg_path = get_configuration("telegram")
    path = REPO_PATH + os.path.join(cfg_path["subscribed_users_path"])

    try:
        if not os.path.exists(path):
            os.makedirs(path)

        db = TinyDB(os.sep.join([path, cfg_path["subscribed_users_filename"]]))
        item = {'userId': user_id, 'firstname': firstname, 'lastname': lastname, 'type': 'basic',
                'notification': 'True'}
        _LOGGER.debug("register_new_user" + str(item))
        db.insert(item)
        return True

    except Exception as e:
        _LOGGER.info(e)
        return False


def update_user_entry(user_id, field, value) -> bool:
    read_successful, cfg_path = get_configuration("telegram")
    path = REPO_PATH + os.path.join(cfg_path["subscribed_users_path"])

    try:
        db = TinyDB(os.sep.join([path, cfg_path["subscribed_users_filename"]]))
        db_field = Query()
        db.update({field: value}, db_field.userId == user_id)
        return True

    except Exception as e:
        _LOGGER.info(e)
        return False
