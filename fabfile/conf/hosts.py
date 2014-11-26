from fabric.api import env
from fabfile.amazonctl.amazon_ip import *
import pytz

env.db_node_count = "2"
env.ycsb_node_count = "2"

# env.ycsb_ami = "ami-6e7bd919"
# env.db_ami = "ami-6e7bd919"
# # env.management_ami = "ami-6e7bd919"

env.ami = {
    'YCSB': 'ami-6e7bd919',
    'DB': 'ami-6e7bd919',
    'DB_MAN': 'ami-6e7bd919'
}
env.instance_type = {
    'YCSB': 't2.micro',
    'DB': 't2.micro',
    'DB_MAN': 't2.micro'
}

ycsb_ec2_user = 'ec2-user'
env.user = ycsb_ec2_user
env.key_name = 'datalabs-dsc1'
env.key_filename = env.key_name + '.pem'
env.security_group = 'my-eu-sec-group'
env.show = ['debug']
env.connection_attempts = 5

# hosts timezone (required to correctly schedule ycsb tasks)
timezone = pytz.timezone('UTC')


env.roledefs = {'db_public_ip': "1.1.1.1"}
def refresh_roledefs():
    global env
    env.roledefs = {
        'ycsb_private_ip': get_internal_ips("YCSB", True).split(),
        'ycsb_public_ip': get_external_ips("YCSB", True).split(),
        'db_private_ip': get_internal_ips("DB", True).split(),
        'db_public_ip': get_external_ips("DB", True).split(),
        'man_public_ip': get_external_ips("DB_MAN", True).split(),
    }
    return env.roledefs

print 'Initialising Hosts Definition'
env.roledefs = refresh_roledefs()




