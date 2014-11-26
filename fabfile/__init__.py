# from info import df as server_df
# from info import db_status
from fabric.api import env

from amazonctl.ec2 import ec2_up     as ec2_up
from amazonctl.ec2 import ec2_down   as ec2_down
from amazonctl.ec2 import ec2_status as ec2_status
from amazonctl.db  import db_up      as db_up
from amazonctl.db  import db_down    as db_down

from ycsb import load                   as ycsb_load
from ycsb import run_workload           as ycsb_run
from ycsb import status                 as ycsb_status
from ycsb import get_log                as ycsb_get
from ycsb import deploy                 as ycsb_deploy
from ycsb import kill                   as ycsb_kill
from ycsb import clean_logs             as ycsb_clean
from ycsb import intialise_tables       as ycsb_inittables

from ycsb import test                   as ycsb_test
from amazonctl.ec2 import test          as ec2_test
from amazonctl.db import test           as db_test


