from fabric.api import env
from fabfile.amazon_ip import *
from fabric.api import env
import pytz

env.db_node_count="2"
env.ycsb_node_count="2"

env.ycsb_ami="ami-6e7bd919"

env.user = 'ec2-user'
env.key_filename = 'datalabs-dsc1.pem'

env.db_instance_type="m1.large"
env.ycsb_instance_type="t2.micro"



env.show = ['debug']

#hosts timezone (required to correctly schedule ycsb tasks)
timezone = pytz.timezone('UTC')

def generate_roledefs():
    return {
        'client_private_ip': get_internal_ips("YCSB").split(),
        'client': get_external_ips("YCSB").split(),
        'server_private_ip': get_internal_ips("DB").split(),
        'server': get_external_ips("DB").split(),
        'server_man': get_external_ips("DB_MAN").split(),
        }


env.roledefs = generate_roledefs()




