from fabric.api import env
from fabfile.amazon_ip import *
import pytz

env.db_node_count = "2"
env.ycsb_node_count = "2"

env.ycsb_ami = "ami-6e7bd919"

ycsb_ec2_user = 'ec2-user'
env.user = ycsb_ec2_user
env.key_name = 'datalabs-dsc1'
env.key_filename = env.key_name + '.pem'
env.security_group = 'my-eu-sec-group'

env.ycsb_instance_type = "t2.micro"

env.show = ['debug']

# hosts timezone (required to correctly schedule ycsb tasks)
timezone = pytz.timezone('UTC')

def refresh_roledefs():
    global env
    env.roledefs =  {
        'ycsb_private_ip': get_internal_ips("YCSB",True).split(),
        'ycsb_public_ip': get_external_ips("YCSB",True).split(),
        'db_private_ip': get_internal_ips("DB",True).split(),
        'db_public_ip': get_external_ips("DB",True).split(),
        'man_public_ip': get_external_ips("DB_MAN",True).split(),
    }
refresh_roledefs()




