import os
import re
import operator
import group_parser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = group_parser.data_table()

print data

#reuse the columns datastructure to keep the column names
frame = group_parser.columns.copy()
for key, value in frame.items():
    frame[key] = []

#Transpose as panda works by column not by row
for row in data:
    for key, value in frame.items():
        index = group_parser.columns[key]['index']
        frame[key].append(row[index])

#convert each column to a panda series with the correct datatype
for key, value in frame.items():
    col_info = group_parser.columns[key]
    type = col_info['dtype']

    #convert any ''->'0' for numeric columns
    if type is 'float32':
        for index, item in enumerate(value):
            if item == '':
                value[index] = '0'

    frame[key] = pd.Series(value, dtype=type)


df = pd.DataFrame(frame)
# print df

# print df.groupby('key-start').aggregate(sum)

