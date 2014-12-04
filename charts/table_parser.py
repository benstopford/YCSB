import os
import re

number = 0


def increment():
    global number
    current = number
    number += 1
    return current


column_defs = {'node': {'index': increment(), 'Name': 'Node Id', 'dtype': 'object'},
           'date': {'index': increment(), 'Name': 'Date', 'dtype': 'object'},
           'time': {'index': increment(), 'Name': 'Time', 'dtype': 'object'},
           'db': {'index': increment(), 'Name': 'DB', 'dtype': 'object'},
           'workload': {'index': increment(), 'Name': 'Workload', 'dtype': 'object'},
           'key-start': {'index': increment(), 'Name': 'Keyspace Start Point', 'dtype': 'int32'},
           'throughput': {'index': increment(), 'Average Throughput(ops/sec)': 'Node Id', 'dtype': 'float32'},
           'insert-lat': {'index': increment(), 'Name': 'InsertLatency(us)', 'dtype': 'float32'},
           'read-lat': {'index': increment(), 'Name': 'ReadLatency(us)', 'dtype': 'float32'},
           'update-lat': {'index': increment(), 'Name': 'UpdateLatency(us)', 'dtype': 'float32'},
           'recordcount': {'index': increment(), 'Name': 'RecordCount', 'dtype': 'int32'},
           'fieldcount': {'index': increment(), 'Name': 'FieldCount', 'dtype': 'int32'},
           'fieldlength': {'index': increment(), 'Name': 'FieldLength(B)', 'dtype': 'int32'},
           'insertcount': {'index': increment(), 'Name': 'InsertCount', 'dtype': 'int32'},
           'operations': {'index': increment(), 'Name': 'Operations', 'dtype': 'float32'}
}


def data_table(dir):
    table = []
    for file in os.listdir(dir):
        if file.endswith(".out"):
            result = [""] * len(column_defs.keys())
            file_details = file.split('_')

            # Node ID
            p = re.compile('[-].*')
            node = p.finditer(file_details[3]).next().group()[1:]
            result[column_defs['node']['index']] = node[:-4]

            # Date
            result[column_defs['date']['index']] = file_details[0]

            # DB
            result[column_defs['db']['index']] = file_details[2]

            # Format time
            result[column_defs['time']['index']] = file_details[1].replace('-', ':')

            #Workload
            file_details[3] = file_details[3].replace('.out', '')
            result[column_defs['workload']['index']] = p.sub('', file_details[3])

            f = open(os.path.join(dir, file))
            for line in f:
                if line.startswith('Command line: '):
                    p = re.compile("insertstart=[0-9]*")
                    result[column_defs['key-start']['index']] = p.finditer(line).next().group().split('=')[1]

                    p = re.compile("recordcount=[0-9]*")
                    result[column_defs['recordcount']['index']] = p.finditer(line).next().group().split('=')[1]

                    p = re.compile("fieldcount=[0-9]*")
                    result[column_defs['fieldcount']['index']] = p.finditer(line).next().group().split('=')[1]

                    p = re.compile("fieldlength=[0-9]*")
                    result[column_defs['fieldlength']['index']] = p.finditer(line).next().group().split('=')[1]

                    if 'insertcount' in line:
                        p = re.compile("insertcount=[0-9]*")
                        result[column_defs['insertcount']['index']] = p.finditer(line).next().group().split('=')[1]

                if line.startswith('[OVERALL]') and 'Throughput' in line:
                    result[column_defs['throughput']['index']] = line.split(", ")[-1][:-1]

                if line.startswith('[OVERALL]') and 'Operations' in line:
                    result[column_defs['operations']['index']] = line.split(", ")[-1][:-1]

                if line.startswith('[INSERT]') and 'AverageLatency' in line:
                    result[column_defs['insert-lat']['index']] = line.split(", ")[-1][:-1]

                if line.startswith('[READ]') and 'AverageLatency' in line:
                    result[column_defs['read-lat']['index']] = line.split(", ")[-1][:-1]

                if line.startswith('[UPDATE]') and 'AverageLatency' in line:
                    result[column_defs['update-lat']['index']] = line.split(", ")[-1][:-1]

            table.append(result)

    return table;