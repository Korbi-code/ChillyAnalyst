# !/usr/bin/env python
# -*- coding:utf-8 -*-

# import module
import os
import collections
import plotly
import plotly.graph_objects as go
import configparser
import sys
from pathlib import Path
import os
import shutil
import datetime

# Define global REPO_PATH
REPO_PATH = str((Path(sys.argv[0]).parents[1]).resolve())

# config handler
DATACONTAINER_CFG = configparser.ConfigParser()
configFilePath = REPO_PATH + r'/config/config.cfg'
DATACONTAINER_CFG.read(configFilePath)


class DataContainer:
    def __init__(self):
        self.mode = 'IDLE'
        self.buffer_length = int(DATACONTAINER_CFG.get('data_container', 'pre_value_buffer'))
        self.value_buffer = collections.deque(maxlen=self.buffer_length)
        for i in range(self.buffer_length):
            self.value_buffer.append(0)
        self.data_container = []
        self.data_path = REPO_PATH + DATACONTAINER_CFG.get('data_container', 'measurement_data_path')
        self.file_name = DATACONTAINER_CFG.get('data_container', 'file_name') + '.html'
        self.path_to_file = str(self.data_path) + str(self.file_name)
        Path(self.data_path).mkdir(parents=True, exist_ok=True)
        self.start_date = 0
        self.end_date = 0

    def add_new_value(self, value):
        if self.mode == 'IDLE':
            self.value_buffer.append(value)
        elif self.mode == 'ACQUISITION':
            self.data_container.append(value)

    def enable_acquisition(self):
        self.data_container.clear()
        for elem in self.value_buffer:
            self.data_container.append(elem)
        self.mode = 'ACQUISITION'
        self.start_date = datetime.datetime.now()

    def disable_acquisition(self):
        self.mode == 'IDLE'
        self.end_date = datetime.datetime.now()

    def create_graph(self):

        y = self.data_container
        x = []
        size_of_pre_value_buffer = int(DATACONTAINER_CFG.get('data_container', 'pre_value_buffer'))
        time_delta_in_idle = int(DATACONTAINER_CFG.get('parameter', 'PARAM_IDLE_TICK_RATE'))
        time_delta_in_measure = int(DATACONTAINER_CFG.get('parameter', 'PARAM_MEASURE_TICK_RATE'))
        for index, value in enumerate(y):
            if index < size_of_pre_value_buffer:
                x.append(self.start_date - datetime.timedelta(
                    seconds=((size_of_pre_value_buffer - index) * int(time_delta_in_idle))))
            elif index == size_of_pre_value_buffer:
                x.append(self.start_date)
            else:
                x.append(x[-1] + datetime.timedelta(seconds=int(time_delta_in_measure)))

        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)
        else:
            for filename in os.listdir(self.data_path):
                file_path = os.path.join(self.data_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

        if self.start_date != 0:
            title_message = 'Waschvorgang vom ' + str(self.start_date.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            title_message = 'Kein Waschvorgang erkannt'

        plotly.offline.plot({
            "data": [go.Scatter(x=x, y=y)],
            "layout": go.Layout(title=title_message,
                                yaxis=dict(
                                    title="Leistung [W]"
                                ),
                                xaxis=dict(
                                    title="Uhrzeit"
                                ))
        }, auto_open=True, image='png', filename=self.path_to_file, include_plotlyjs='cdn')

        return True

    def get_html(self):
        if os.path.isfile(self.path_to_file):
            return self.path_to_file
        else:
            return False
