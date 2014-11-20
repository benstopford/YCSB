from fabric.api import env
from fabfile.amazon_ip import *
from fabric.api import env
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


def generate_roledefs():
    return {
        'ycsb_private_ip': get_internal_ips("YCSB").split(),
        'ycsb_public_ip': get_external_ips("YCSB").split(),
        'db_private_ip': get_internal_ips("DB").split(),
        'db_public_ip': get_external_ips("DB").split(),
        'man_public_ip': get_external_ips("DB_MAN").split(),
    }


env.roledefs = generate_roledefs()




