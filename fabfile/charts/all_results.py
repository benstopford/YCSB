import operator

import table_parser
from table_parser import column_defs


"""Dumps out a table of the raw data by node"""
header = sorted(column_defs.items(), key=operator.itemgetter(1))

print "\t".join([i[0] for i in header])
for line in table_parser.data_table("../logs"):
    print "\t".join(line)




