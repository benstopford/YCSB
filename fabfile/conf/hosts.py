from fabric.api import env as fabric_env
from fabfile.amazonctl.amazon_ip import *
import pytz

_amz_linux_ebs_backed = 'ami-6e7bd919'
_amz_linux_instance_store = 'ami-0318e374'

#*********** General Settings ***************

db_node_count = "1"
ycsb_node_count = "1"

testing = True
use_instance_store = True

enable_copperegg_monitoring = True


#*********** EC2 Settings ***************

#For testing use the smallest instances (which require EBS storage)

#Free servers
instance_type = {
    'YCSB': 't2.micro',
    'DB': 't2.micro',
    'DB_MAN': 't2.micro'
}
ebs_disk_allocation = 8
ami = {
    'YCSB': _amz_linux_ebs_backed,
    'DB': _amz_linux_ebs_backed,
    'DB_MAN': _amz_linux_ebs_backed
}

instance_store_root_dir = '/media/ephemeral0'
if(use_instance_store):
    #cheapest servers with instance storage
    instance_type = {
        'YCSB': 'm3.medium',
        'DB': 'm3.medium',
        'DB_MAN': 'm3.medium'
    }
    ami = {
        'YCSB': _amz_linux_instance_store,
        'DB': _amz_linux_instance_store,
        'DB_MAN': _amz_linux_instance_store
    }

#For real work use larger instances and switch to instance storage
if not testing:
    #decent servers
    instance_type = {
        'YCSB': 't2.small',
        'DB': 'm3.large',
        'DB_MAN': 'm3.medium'
    }
    ami = {
        'YCSB': _amz_linux_instance_store,
        'DB': _amz_linux_instance_store,
        'DB_MAN': _amz_linux_instance_store
    }
    use_instance_store = True # if false specify ebs_disk_allocation
    ebs_disk_allocation = 32

ycsb_ec2_user = 'ec2-user'
key_name = 'datalabs-dsc1'
security_group = 'my-eu-sec-group'

#*********** Fabric Settings ***************
fabric_env.user = ycsb_ec2_user
fabric_env.key_filename = key_name + '.pem'
fabric_env.show = ['debug']
fabric_env.connection_attempts = 5
fabric_env.roledefs = {'db_public_ip': "1.1.1.1"}
fabric_env.roledefs = {
    'ycsb_private_ip': get_internal_ips("YCSB", True).split(),
    'ycsb_public_ip': get_external_ips("YCSB", True).split(),
    'db_private_ip': get_internal_ips("DB", True).split(),
    'db_public_ip': get_external_ips("DB", True).split(),
    'man_public_ip': get_external_ips("DB_MAN", True).split()
}


#*********** Other Settings ***************

# hosts timezone (required to correctly schedule ycsb tasks)
timezone = pytz.timezone('UTC')





