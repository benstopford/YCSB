# from info import df as server_df
# from info import db_status


from amazon import amazon_start      as ec2_up
from amazon import amazon_terminate  as ec2_down
from amazon import amazon_status  as ec2_status

from ycsb import start_db_man           as ycsb_start_db_man
from ycsb import start_db               as ycsb_start_db
from ycsb import load                   as ycsb_load
from ycsb import run_workload           as ycsb_run
from ycsb import status                 as ycsb_status
from ycsb import get_log                as ycsb_get
from ycsb import deploy                 as ycsb_deploy
from ycsb import kill                   as ycsb_kill
from ycsb import kill_db                as ycsb_kill_db
from ycsb import kill_db_man            as ycsb_kill_db_man
from ycsb import clean_logs             as ycsb_clean
from ycsb import test                   as ycsb_test
from ycsb import intialise_tables       as ycsb_inittables


from mongodb import mongos_restart
from mongodb import mongos_stop

from aerospike import aerospike_start
from aerospike import aerospike_stop

