import panda_parser
import table_parser

dir = '../../logs'

# Create the raw table from the log files
raw = table_parser.data_table(dir)

# Convert to panda
df = panda_parser.convert_to_panda(raw, table_parser.column_defs)

print df