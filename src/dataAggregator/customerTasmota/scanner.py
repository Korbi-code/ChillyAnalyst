# !/usr/bin/env python
# -*- coding:utf-8 -*-

# imports
import requests
import json
import time


#todo delete main and create scanner function and device object
if __name__ == '__main__':
    while 1:
        r = requests.get(url='http://192.168.188.40/cm?cmnd=Status%208')
        json_con = r.json()
        print(json_con["StatusSNS"]["ENERGY"]["Power"])
        time.sleep(1)