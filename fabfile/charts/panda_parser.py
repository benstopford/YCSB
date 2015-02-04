import pandas as pd


def convert_to_panda(data_table, columns):
    """
    :param data_table: row based table represented as a list of lists
    :param columns: map definining column definitions of the form:
            {'key': {'index': 0, 'Name': 'columnB', 'dtype': 'float'},
               'two': ...}
    :return: this mapped to a panda data structure
    """
    # reuse the columns datastructure to keep the column names
    frame = columns.copy()
    for key, value in frame.items():
        frame[key] = []

    # Transpose as panda works by column not by row
    for row in data_table:
        for key, value in frame.items():
            index = columns[key]['index']
            frame[key].append(row[index])

    #convert each column to a panda series with the correct datatype
    for key, value in frame.items():
        col_info = columns[key]
        type = col_info['dtype']

        #convert any ''->'0' for numeric columns
        if type in ['float32', 'float64', 'int32', 'int64']:
            for index, item in enumerate(value):
                if item == '':
                    value[index] = '0'

        frame[key] = pd.Series(value, dtype=type)

    return pd.DataFrame(frame)