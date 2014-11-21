from subprocess import *
import time
from fabric.api import *
from amazon_ip import *
from conf.hosts import ycsb_ec2_user

dir = "fabfile/amazonctl/"


def wait_for_tagged_hosts_to_start(tag, count):
    while len(get_external_ips(tag).split()) < int(count):
        print "Waiting for %s hosts to start. Currently %s" % (count, len(get_external_ips(tag).split()))
        time.sleep(1)

    print '%s %s hosts started' % (count, tag)

    # Test the ssh connection with retries
    # Use explicit execute call rather than fabric role defs as this method works for any tag
    execute(
        test_connection_with_wait,
        hosts=get_external_ips(tag).split()
    )

def test_connection_with_wait():
    with settings(connection_attempts=100, timeout=5):
        run("echo 'testing connection'")


def reboot_instances(tag):
    ids = get_instance_ids_for_tag(tag).split()
    local("aws ec2 reboot-instances --instance-ids %s" % " ".join(ids))


def set_db_ssh_user(database):
    # User must be set at database level so override global
    global env
    if 'ec2user' in database:
        env.user = database['ec2user']


def set_ycsb_ssh_user():
    # set user back to ycsb user
    env.user = ycsb_ec2_user


def amazon_terminate():
    out = Popen(["%sec2terminate" % dir], stdout=PIPE).communicate()[0]
    print out


def amazon_status():
    out = Popen(["%sec2status" % dir], stdout=PIPE).communicate()[0]
    print out








