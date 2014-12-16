from fabric.api import *
from fabfile.util.print_utils import emphasis
from fabfile.conf.hosts import addresses, running_db_node_count, running_ycsb_node_count

@parallel
def install_mongodb():
    """Installs MongoDB"""
    print emphasis('Installing MongoDB')

    file = "/etc/yum.repos.d/mongodb.repo"
    sudo("yum -y update")
    sudo("rm -f " + file)
    sudo("touch " + file)
    sudo("chmod 777 " + file)
    sudo('echo "[mongodb] \n'
         'name = name=MongoDB Repository\n'
         'baseurl = http://downloads-distro.mongodb.org/repo/redhat/os/x86_64/\n'
         'enabled = 1\n'
         'gpgcheck = 0" '
         '> ' + file)
    sudo("chmod 644 " + file)
    sudo('yum -y install  mongodb-org')

    print '********Mongo is installed********'



def install():
    execute(
        install_mongodb,
        hosts=addresses()['db_public_ip']+addresses()['man_public_ip']
    )