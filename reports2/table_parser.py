import os
import re

number = 0


def increment():
    global number
    current = number
    number += 1
    return current


columns = {'node': {'index': increment(), 'Name': 'Node Id', 'dtype': 'object'},
           'date': {'index': increment(), 'Name': 'Date', 'dtype': 'object'},
           'time': {'index': increment(), 'Name': 'Time', 'dtype': 'object'},
           'db': {'index': increment(), 'Name': 'DB', 'dtype': 'object'},
           'workload': {'index': increment(), 'Name': 'Workload', 'dtype': 'object'},
           'key-start': {'index': increment(), 'Name': 'Keyspace Start Point', 'dtype': 'float32'},
           'throughput': {'index': increment(), 'Average Throughput(ops/sec)': 'Node Id', 'dtype': 'float32'},
           'insert-lat': {'index': increment(), 'Name': 'InsertLatency(us)', 'dtype': 'float32'},
           'read-lat': {'index': increment(), 'Name': 'ReadLatency(us)', 'dtype': 'float32'},
           'update-lat': {'index': increment(), 'Name': 'UpdateLatency(us)', 'dtype': 'float32'},
           'recordcount': {'index': increment(), 'Name': 'RecordCount', 'dtype': 'float32'},
           'fieldcount': {'index': increment(), 'Name': 'FieldCount', 'dtype': 'float32'},
           'fieldlength': {'index': increment(), 'Name': 'FieldLength(B)', 'dtype': 'float32'}
}


def data_table(dir):
    table = []
    for file in os.listdir(dir):
        if file.endswith(".out"):
            result = [""] * len(columns.keys())
            file_details = file.split('_')

            # Node ID
            p = re.compile('[-].*')
            node = p.finditer(file_details[3]).next().group()[1:]
            result[columns['node']['index']] = node[:-4]

            # Date
            result[columns['date']['index']] = file_details[0]

            # DB
            result[columns['db']['index']] = file_details[2]

            # Format time
            result[columns['time']['index']] = file_details[1].replace('-', ':')

            #Workload
            file_details[3] = file_details[3].replace('.out', '')
            result[columns['workload']['index']] = p.sub('', file_details[3])

            f = open(os.path.join(dir, file))
            for line in f:
                if line.startswith('Command line: '):
                    p = re.compile("insertstart=[0-9]*")
                    result[columns['key-start']['index']] = p.finditer(line).next().group().split('=')[1]

                    p = re.compile("recordcount=[0-9]*")
                    result[columns['recordcount']['index']] = p.finditer(line).next().group().split('=')[1]

                    p = re.compile("fieldcount=[0-9]*")
                    result[columns['fieldcount']['index']] = p.finditer(line).next().group().split('=')[1]

                    p = re.compile("fieldlength=[0-9]*")
                    result[columns['fieldlength']['index']] = p.finditer(line).next().group().split('=')[1]

                if line.startswith('[OVERALL]') and 'Throughput' in line:
                    result[columns['throughput']['index']] = line.split(", ")[-1][:-1]

                if line.startswith('[INSERT]') and 'AverageLatency' in line:
                    result[columns['insert-lat']['index']] = line.split(", ")[-1][:-1]

                if line.startswith('[READ]') and 'AverageLatency' in line:
                    result[columns['read-lat']['index']] = line.split(", ")[-1][:-1]

                if line.startswith('[UPDATE]') and 'AverageLatency' in line:
                    result[columns['update-lat']['index']] = line.split(", ")[-1][:-1]

            table.append(result)

    return table;