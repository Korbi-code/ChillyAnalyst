# !/usr/bin/env python
# -*- coding:utf-8 -*-

# import module
import os
import collections
import plotly.graph_objects as go
from pathlib import Path
import configparser

# config handler
DATACONTAINER_CFG = configparser.ConfigParser()
configFilePath = r'../config/config.cfg'
DATACONTAINER_CFG.read(configFilePath)

class DataContainer:
    def __init__(self):
        self.mode = 'IDLE'
        self.buffer_length = int(DATACONTAINER_CFG.get('data_container', 'pre_value_buffer'))
        self.value_buffer = collections.deque(maxlen=self.buffer_length)
        for i in range(self.buffer_length):
            self.value_buffer.append(0)
        self.data_container = []
        self.data_path = DATACONTAINER_CFG.get('data_container', 'measurement_data_path')
        self.file_name = DATACONTAINER_CFG.get('data_container', 'file_name')
        self.path_to_file = str(self.data_path) + str(self.file_name)
        Path(self.data_path).mkdir(parents=True, exist_ok=True)

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

    def disable_acquisition(self):
        self.mode == 'IDLE'

    def create_graph(self, value_resolution):

        y = [element * value_resolution for element in self.data_container]
        x = list(range(len(y)))
        fig = go.Figure()

        try:
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                name='<b>No</b> Gaps',
                connectgaps=True,
            ))
            fig.update_layout(title='Washi Washi Run',
                                yaxis = dict(
                                    title="Power [W]"
                                ),
                                xaxis = dict(
                                    title="Ticks"
                                ))
            fig.show()

            if os.path.exists(self.data_path):
                try:
                    fig.write_image(self.path_to_file)
                    return True
                except:
                    return False
        except:
            return False

    def get_png(self):
        if os.path.isfile(self.path_to_file):
            return self.path_to_file
        else:
            return False
