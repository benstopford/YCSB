import shutil
import numpy
import panda_parser
import table_parser
import pandas as pd
import math


def enum(**enums):
    return type('Enum', (), enums)


Workloads = enum(LOAD='load', A='workloada', B='workloadb', C='workloadc')


def agg_throughput(df, workload):
    grouped = df[df.workload == workload].groupby('key-start')
    agg = grouped.agg('mean')
    tp = agg['throughput']
    return tp


def throughput(dir):
    # Create the raw table from the log files
    raw = table_parser.data_table(dir)

    # Convert to panda
    df = panda_parser.convert_to_panda(raw, table_parser.column_defs)

    # Calculate how much data is added per 'run'
    data_per_iteration = df['recordcount'].unique().mean()
    + df['fieldcount'].unique().mean()
    + df['fieldlength'].unique().mean()
    + df['operations'].unique().mean()

    # Define the x axes as the incremental data we are adding
    iterations = len(df['key-start'].unique()) + 1
    x_axis = list(numpy.arange(data_per_iteration, data_per_iteration * iterations, data_per_iteration))
    x_axis = [int(i) for i in x_axis]
    x_axis.insert(0, 'x')

    #Define the columns we want in the chart and merge them into a single table
    #(merging on the key which is key-start)
    merged = pd.concat([
                           agg_throughput(df, Workloads.LOAD),
                           agg_throughput(df, Workloads.A)
                       ], axis=1)
    merged.columns = ['load-throughput', 'wla-throughput']

    #Pull out each column, give it a name, format the output string
    plots = (x_axis,)
    for column in merged.columns:
        plot = list(merged[column])
        plot.insert(0, column)
        plot = [0 if isinstance(x, numpy.float32) and math.isnan(x) else x for x in plot]
        plots += (plot,)

    output = "x:'x', columns:[%s,%s,%s]" % plots

    return output


def insert_data_into_chart(data):
    base = 'charts/latest/data.js.template'
    out = 'charts/latest/data.js'

    print 'generating chart data: ' + out
    print 'data: ' + data

    with open(out, "wt") as fout:
        with open(base, "rt") as fin:
            for line in fin:
                if '#data#' in line:
                    line = line.replace('#data#', data)
                fout.write(line)
                print line


