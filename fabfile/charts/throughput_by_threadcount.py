import pandas as pd

import panda_parser
import table_parser


dir = '../../logs'

# Create the raw table from the log files
raw = table_parser.data_table(dir)

# Convert to panda
df = panda_parser.convert_to_panda(raw, table_parser.column_defs)

print df
print ''

grouped = df.groupby('threadcount')
agg = grouped.agg('mean')
tp = agg['throughput']

print 'Throughput (ops/sec) by threadcount (higher is better)'
print tp
print ''

grouped = df.groupby('threadcount')
agg = grouped.agg('mean')
tp = agg['insert-lat']

grouped = df.groupby('threadcount')
agg = grouped.agg('mean')
tp2 = agg['update-lat']

grouped = df.groupby('threadcount')
agg = grouped.agg('mean')
tp3 = agg['read-lat']

merged = pd.concat([
                       tp,
                       tp2,
                       tp3
                   ], axis=1)

print 'Latency (us) by threadcount (lower is better)'
print merged
print ''





grouped = df.groupby('threadcount')
agg = grouped.agg('mean')
tp = agg['runtime']

print 'Av Runtime (s) by threadcount (lower is better)'
print tp


grouped = df.groupby('threadcount')
agg = grouped.agg('max')
tp = agg['reconnections']

print 'Max Reconnections by threadcount -> watch these!!'
print tp
print ''





print 'nb we dont clear the data between runs so later runs my have worse performance for that reason.'
