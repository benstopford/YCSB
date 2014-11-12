from fabric.api import env

env.db_node_count="1"
env.ycsb_node_count="1"

env.ycsb_ami="ami-6e7bd919"

casssandra="ami-8932ccfe"
mongo="ami-a42884d3"

env.db_ami=mongo