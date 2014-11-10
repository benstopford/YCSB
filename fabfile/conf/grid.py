from fabric.api import env

env.cassandra_node_count="3"
env.ycsb_node_count="6"

env.ycsb_ami="ami-6e7bd919"
env.casssandra_ami="ami-7f33cd08"