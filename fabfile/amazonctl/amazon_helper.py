from subprocess import *
import time
from fabric.api import settings, run, local, execute
from fabfile.conf.hosts import ycsb_ec2_user
from amazon_ip import *
from socket import error as socket_error

dir = "fabfile/amazonctl/"


def wait_for_tagged_hosts_to_start(tag, count):
    while len(get_external_ips(tag).split()) < int(count):
        print "Waiting for %s hosts to start. Currently %s" % (count, len(get_external_ips(tag).split()))
        time.sleep(1)

    print '%s %s hosts are running' % (count, tag)

    # Test the ssh connection with retries
    # Use explicit execute call rather than fabric role defs as this method works for any tag
    execute(
        test_connection_with_wait,
        hosts=get_external_ips(tag).split()
    )

def test_connection_with_wait():
    with settings(connection_attempts=30, timeout=10, warn_only=True): #5mins
        while True:
            try:
                run("echo 'Testing ssh connection...'")
            except socket_error:
                continue
            break

def reboot_instances(tag):
    ids = get_instance_ids_for_tag(tag).split()
    local("aws ec2 reboot-instances --instance-ids %s" % " ".join(ids))
    time.sleep(5)


def set_db_ssh_user(database):
    # User must be set at database level so override global
    global env
    if 'ec2user' in database:
        env.user = database['ec2user']


def set_ycsb_ssh_user():
    # set user back to ycsb user
    env.user = ycsb_ec2_user






