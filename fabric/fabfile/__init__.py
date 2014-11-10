# from info import df as server_df
# from info import db_status


from amazon import amazon_start      as ec2_up
from amazon import amazon_terminate  as ec2_down

from ycsb import load         as ycsb_load
from ycsb import run_workload as ycsb_run
from ycsb import status       as ycsb_status
from ycsb import get_log      as ycsb_get
from ycsb import deploy       as ycsb_deploy
from ycsb import kill         as ycsb_kill
from ycsb import clean_logs   as ycsb_clean
from ycsb import test   as ycsb_test


from mongodb import mongos_restart
from mongodb import mongos_stop

from aerospike import aerospike_start
from aerospike import aerospike_stop

