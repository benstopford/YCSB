from fabric.api import env as fabric_env
from fabfile.amazonctl.amazon_ip import *
import pytz

_amz_linux_ebs_backed_para = 'ami-6e7bd919'
_amz_linux_instance_store_para = 'ami-0318e374'
_amz_linux_instance_store_hvm = 'ami-0f21df78'

# *********** General Settings ***************
host_counts = {
    'db': 2,
    'ycsb': 6
}

testing = False
use_instance_store = False

enable_copperegg_monitoring = True


# *********** EC2 Settings ***************

#For testing use the smallest instances (which require EBS storage)

#Free servers
instance_type = {
    'YCSB': 't2.micro',
    'DB': 't2.micro',
    'DB_MAN': 't2.micro'
}
ebs_disk_allocation = {
    'YCSB': 8,
    'DB': 8,
    'DB_MAN': 8
}
ami = {
    'YCSB': _amz_linux_ebs_backed_para,
    'DB': _amz_linux_ebs_backed_para,
    'DB_MAN': _amz_linux_ebs_backed_para
}

instance_store_root_dir = '/media/ephemeral0'
if use_instance_store and testing:
    #cheapest servers with instance storage
    instance_type = {
        'YCSB': 't2.small',
        'DB': 'm3.medium',
        'DB_MAN': 'm3.medium'
    }
    ami = {
        'YCSB': _amz_linux_ebs_backed_para,
        'DB': _amz_linux_instance_store_para,
        'DB_MAN': _amz_linux_instance_store_para
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
        'YCSB': _amz_linux_ebs_backed_para,
        'DB': _amz_linux_ebs_backed_para,
        'DB_MAN': _amz_linux_ebs_backed_para
    }
    ebs_disk_allocation = {
        'YCSB': 8,
        'DB': 100,
        'DB_MAN': 8
    }

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





