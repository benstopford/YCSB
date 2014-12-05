import subprocess
from fabric.api import *
from fabfile.amazonctl.amazon_helper import *
from fabfile.helpers import get_db
from fabfile.amazonctl.amazon_ip import *
from fabfile.conf.machine_config import core_machine_settings
from fabfile.util.print_utils import emphasis
import time
from fabfile.conf.hosts import db_node_count, ycsb_node_count, ami, instance_type, key_name, security_group, \
    use_instance_store, ebs_disk_allocation


def start(tag, node_count):
    """Starts defined database instances if they are not already running based on a tag and an expected count to be running"""
    current = len(get_external_ips(tag).split())

    print emphasis('Starting nodes for tag: "%s"' % tag)

    if current >= node_count:
        print "Not starting new %s nodes as there are already %s running." % (tag, current)
        return

    if node_count > current > 0:
        node_count = node_count - current
        print "There are already %s %s nodes running so we will only start %s additional ones" % (
            current, tag, node_count)

    start_db_ec2_instance(node_count, tag)


def configure_machine_and_reboot(tag, node_count):
    print emphasis('Executing pre-reboot-settings for %s' % tag)

    wait_for_tagged_hosts_to_start(tag, node_count)

    # Add machine specific config such as ulimits
    execute(
        core_machine_settings,
        hosts=get_external_ips(tag).split()
    )
    reboot_instances(tag)


def start_db_ec2_instance(node_count, tag):
    if use_instance_store:
        print 'Starting server with instance store'
        command = ["aws", "ec2", "run-instances",
                   "--count=" + str(node_count),
                   "--image-id=" + ami[tag],
                   "--instance-type=" + instance_type[tag],
                   "--key-name=" + key_name,
                   "--security-groups=" + security_group
        ]
    else:
        print 'starting server using ebs'
        disk = '8'
        if tag is 'YCSB':
            disk = str(ebs_disk_allocation)

        # use shell script to get around awkward json argument
        command = [dir + "ec2runinstance", str(node_count), ami[tag], instance_type[tag], key_name, security_group,
                   disk]

    print command
    out = subprocess.check_output(command)

    # Tag the instances we created - TODO: replace with regex
    for line in out.split("\n"):
        if line.startswith("INSTANCES"):
            for word in line.split("\t"):
                if (word.startswith("i-")):
                    subprocess.call([dir + "ec2tag", word, tag])


def ec2_up(db):
    include_management_node = get_db(db)['has_management_node']

    dbs = [('DB', int(db_node_count)),
           ('YCSB', int(ycsb_node_count))]

    if include_management_node:
        dbs += [('DB_MAN', 1)]

    print emphasis('booting nodes for tags %s' % ", ".join([x[0] for x in dbs]))

    # Start eveything up first (as slow)
    for tag in dbs:
        start(tag[0], tag[1])

    # Configure
    for tag in dbs:
        configure_machine_and_reboot(tag[0], tag[1])

    # Check started
    print emphasis("waiting for hosts to start after reboot - ctr-c if you don't want to wait")
    for tag in dbs:
        wait_for_tagged_hosts_to_start(tag[0], tag[1])


def terminate_running_instances():
    ids = local("aws ec2 describe-instances | grep INSTANCE | awk {'print $8'} | sort | uniq", capture=True).replace(
        '\n', ' ')
    local('aws ec2 terminate-instances --instance-ids %s' % ids)


def wait_for_instance_shutdown():
    running = 'aws ec2 describe-instances | grep STATE | grep -v terminated | grep -v Client.UserInitiatedShutdown | wc -l'
    while int(local(running, capture=True)) > 0:
        time.sleep(1)
        print 'waiting for instances to terminate'


def delete_all_volumes():
    volumes = local("aws ec2 describe-volumes | grep VOLUMES | awk {'print $9'}", capture=True).split("\n")
    for v in volumes:
        if v != '':
            local('aws ec2 delete-volume --volume-id %s' % v)


def ec2_down():
    print emphasis('ec2_down')

    terminate_running_instances()
    wait_for_instance_shutdown()
    delete_all_volumes()


def ec2_status():
    out = Popen([dir + "ec2status"], stdout=PIPE).communicate()[0]
    print out


def test():
    print 'hello'



