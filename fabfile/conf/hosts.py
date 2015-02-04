from fabric.api import env as fabric_env
from fabfile.amazonctl.amazon_ip import get_internal_ips, get_external_ips
from fabfile.util.print_utils import log
import pytz

#***********************************************
# *********** MAIN HOST SETTINGS ***************
#***********************************************

# *********** Set the number of VMs you want to spin up ***************
host_counts = {
    'DB': 2,
    'YCSB': 2,
}

# *********** Set the machine type ***************
profile = 'free'
# profile = 'small'
# profile = 'instance'
# profile = 'medium'

# *********** Copperegg provides a free trial, just sign up ***************
enable_copperegg_monitoring = False




#*******************************************
# *********** OTHER SETTINGS ***************
#*******************************************

# *********** EC2 Settings ***************
_amz_linux_ebs_backed_para = 'ami-6e7bd919'
_amz_linux_instance_store_para = 'ami-0318e374'
_amz_linux_instance_store_hvm = 'ami-0f21df78'

# For testing use the smallest instances (which require EBS storage)

#Free servers
if profile == 'free':
    instance_type = {
        'YCSB': 't2.micro',
        'DB': 't2.micro',
        'DB_MAN': 't2.micro'
    }
    ebs_disk_allocation = {
        'YCSB': 8,
        'DB': 16,
        'DB_MAN': 8
    }
    ami = {
        'YCSB': _amz_linux_ebs_backed_para,
        'DB': _amz_linux_ebs_backed_para,
        'DB_MAN': _amz_linux_ebs_backed_para
    }

if profile == 'small':
    instance_type = {
        'YCSB': 't2.micro',
        'DB': 'm3.medium',
        'DB_MAN': 't2.small'
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

use_instance_store = False
instance_store_root_dir = '/media/ephemeral0'

if profile == 'instance':
    use_instance_store = True
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

#For real work use larger instances on EBS
if profile == 'medium':
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

cache = None


def print_status():
    if cache is None:
        addresses()


def addresses():
    global cache
    if cache == None:
        cache = {
            'ycsb_private_ip': get_internal_ips("YCSB", True).split(),
            'ycsb_public_ip': get_external_ips("YCSB", True).split(),
            'db_private_ip': get_internal_ips("DB", True).split(),
            'db_public_ip': get_external_ips("DB", True).split(),
            'man_public_ip': get_external_ips("DB_MAN", True).split()
        }
    return cache


def refresh_hosts_cache():
    global cache
    cache = None


def running_db_node_count():
    return len(get_internal_ips("DB", True).split())


def running_ycsb_node_count():
    return len(get_internal_ips("YCSB", True).split())


#*********** Fabric Settings ***************
fabric_env.user = ycsb_ec2_user
fabric_env.key_filename = key_name + '.pem'
fabric_env.show = ['debug']
fabric_env.connection_attempts = 5

#*********** Other Settings ***************

# hosts timezone (required to correctly schedule ycsb tasks)
timezone = pytz.timezone('UTC')





