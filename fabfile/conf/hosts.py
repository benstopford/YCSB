from fabric.api import env
import pytz
from fabfile.amazon import *

env.user = 'ec2-user'
env.key_filename = 'datalabs-dsc1.pem'

env.show = ['debug']

env.roledefs = {
    'client_private_ip': get_internal_ips("YCSB").split(),
    'client': get_external_ips("YCSB").split(),
    'server': get_external_ips("DB").split(),
    }

# env.ycsb_run_dir

#hosts timezone (required to correctly schedule ycsb tasks)
timezone = pytz.timezone('UTC')

