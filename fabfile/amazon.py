import subprocess
from fabric.api import *
from amazon_helper import *
from fabfile.helpers import get_db
from conf.hosts import refresh_roledefs
from amazon_ip import *


def start_db_and_management(database):
    """Start both database and management nodes"""

    start(database, 'DB', int(env.db_node_count))

    if database['has_management_node'] in 'True':
        start(database, 'DB_MAN', 1)


def install(database, tag):
    # Add machine specific config such as ulimits
    if 'pre-reboot-settings' in database:
        print 'Executing pre-reboot-settings'
        execute(
            configure_db_instances,
            database,
            hosts=get_external_ips(tag).split()
        )
        reboot_instances(tag)
        wait_for_tagged_hosts_to_start(tag, env.db_node_count)

    if 'start_db_function' in database:
        print 'Executing start_db_function'
        database['start_db_function']()


def start_db_ec2_instance(database, node_count, tag):
    # start db
    command = ["aws", "ec2", "run-instances",
               "--count=" + `node_count`,
               "--instance-type=" + database['instance-type'],
               "--key-name=" + env.key_name,
               "--security-groups=" + env.security_group
    ]
    for key, value in database['ec2_config'].iteritems():
        command.append(key + "=" + value)
    print command
    out = subprocess.check_output(command)
    # Tag the instances we created - TODO: replace with regex
    for line in out.split("\n"):
        if line.startswith("INSTANCES"):
            for word in line.split("\t"):
                if (word.startswith("i-")):
                    subprocess.call(["%sec2tag2" % dir, word, tag])


def start(database, tag, node_count):
    """Starts defined database instances if they are not already running based on a tag and an expected count to be running"""

    print 'Starting %s' % tag

    current = len(get_external_ips(tag).split())

    if current >= node_count:
        print "Not starting new %s nodes as there are already %s running." % (tag, current)
        return

    if node_count > current > 0:
        node_count = node_count - current
        print "There are already %s %s nodes running so we will only start %s additional ones" % (current, tag, node_count)

    start_db_ec2_instance(database, node_count, tag)

    wait_for_tagged_hosts_to_start(tag, node_count)

    refresh_roledefs()

    install(database, tag)


def start_ycsb_instances(): #todo this could be refactored to remove duplication with start db
    node_count = int(env.ycsb_node_count)
    current = len(get_external_ips('YCSB').split())

    if node_count <= current:
        print "Not starting new ycsb nodes as there are already %s running." % current
        return

    if 0 < current < node_count:
        node_count = node_count - current
        print "There are already %s nodes running so we will only start %s additional ones" % (current, node_count)

    command = ["aws", "ec2", "run-instances",
               "--count=" + str(node_count),
               "--image-id=" + env.ycsb_ami,
               "--instance-type=" + env.ycsb_instance_type,
               "--key-name="+env.key_name,
               "--security-groups="+env.security_group
    ]
    print command

    out = subprocess.check_output(command)

    # Tag the instances we just created TODO regex please!
    lines = out.split("\n")
    for line in lines:
        if line.startswith("INSTANCES"):
            for word in line.split("\t"):
                if (word.startswith("i-")):
                    subprocess.call(["%sec2tag2" % dir, word, "YCSB"])

    print 'YCSB nodes have been started. Waiting for them to be accessible (you can Ctrl-C out of this if you wish)'
    refresh_roledefs()
    wait_for_tagged_hosts_to_start('YCSB', node_count)


def configure_db_instances(database):
    commands = database['pre-reboot-settings']
    with settings(connection_attempts=100, timeout=5):
        for command in commands:
            sudo(command)

def amazon_start(db):
    database = get_db(db)

    set_db_ssh_user(database)
    start_db_and_management(database)

    set_ycsb_ssh_user()
    start_ycsb_instances()

    refresh_roledefs()

def test():
    database = get_db('mongodb')
    database['start_db_function']()
