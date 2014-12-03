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

    #Create the raw table from the log files
    raw = table_parser.data_table(dir)

    #Convert to panda
    df = panda_parser.convert_to_panda(raw, table_parser.column_defs)

    #define the x axis as the iteration (which maps to the data loaded)
    x_axis = list(df['key-start'].unique())
    x_axis.insert(0, 'x')

    #Define the columns we want in the chart
    merged = pd.concat([
                           (agg_throughput(df, Workloads.LOAD)),
                           (agg_throughput(df, Workloads.A))
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



