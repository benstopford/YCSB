import subprocess
import time
from fabric.api import env, hosts, roles, run, settings, execute, sudo, local
from fabfile.helpers import get_db
from conf.hosts import generate_roledefs
from amazon_ip import *


dir = "fabfile/amazonctl/"
fabric_variable_bypass = {}

def start_db_instances(database):
    """Start both database and management nodes"""

    start(database, 'DB', int(env.db_node_count))

    if database['has_management_node'] in 'True':
        start(database, 'DB_MAN', 1)


def start(database, tag, node_count):
    """Starts defined database instances if they are not already running based on a tag and an expected count to be running"""

    print 'Starting %s' % tag

    current = len(get_external_ips(tag, False).split())

    if current >= node_count:
        print "Not starting new %s nodes as there are already %s running." % (tag, current)
        return

    if node_count > current > 0:
        node_count = node_count - current
        print "There are already %s %s nodes running so we will only start %s additional ones" % (current, tag, node_count)


    # start db
    command = ["aws", "ec2", "run-instances",
               "--count=" + `node_count`,
               "--instance-type=" + database['instance-type'],
               "--key-name="+env.key_name,
               "--security-groups="+env.security_group
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

    wait_for_tagged_hosts_to_start(tag, node_count)


    #Add machine specific config such as ulimits
    if 'pre-reboot-settings' in database:
        global fabric_variable_bypass
        fabric_variable_bypass = database
        execute(
            configure_db_instances,
            hosts=get_external_ips(tag).split()
        )
        reboot_instances(tag)
        wait_for_tagged_hosts_to_start(tag, node_count)


def start_db_instances_backup(database):
    """Starts defined database instances if they are not already running"""

    node_count = int(env.db_node_count)
    current = len(get_external_ips('DB', False).split())

    # refactor this so that we create the db nodes then create the management nodes and tag them seperately.

    if database['has_management_node'] in 'True':
        node_count += 1

    if current >= node_count:
        print "Not starting new database nodes as there are already %s running." % current
        return

    if node_count > current > 0:
        node_count = node_count - current
        print "There are already %s nodes running so we will only start %s additional ones" % (current, node_count)


    # start db
    command = ["aws", "ec2", "run-instances",
               "--count=" + `node_count`,
               "--instance-type=" + env.db_instance_type,
               "--key-name="+env.key_name,
               "--security-groups="+env.security_group
    ]
    for key, value in database['ec2_config'].iteritems():
        command.append(key + "=" + value)
    print command
    out = subprocess.check_output(command)


    # Tag the instances we created - TODO: replace with regex
    final = ""
    lines = out.split("\n")
    for line in lines:
        if line.startswith("INSTANCES"):
            for word in line.split("\t"):
                if (word.startswith("i-")):
                    subprocess.call(["%sec2tag2" % dir, word, "DB"])
                    final = word

    # Tag the final nods as the management node
    if database['has_management_node'] in 'True':
        subprocess.call(["%sec2tag2" % dir, final, "DB_MAN"])

    wait_for_tagged_hosts_to_start('DB', int(env.db_node_count))

    if database['has_management_node'] in 'True':
        wait_for_tagged_hosts_to_start('DB_MAN', 1)

    #Add machine specific config such as ulimits
    if 'pre-reboot-settings' in database:
        global fabric_variable_bypass
        fabric_variable_bypass = database
        execute(
            configure_db_instances,
            hosts=get_external_ips("DB").split()
        )
        reboot_instances('DB')
        wait_for_tagged_hosts_to_start('DB', node_count)


def start_ycsb_instances():
    node_count = int(env.ycsb_node_count)
    current = len(get_external_ips('YCSB', False).split())

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

    def wait_for_tagged_hosts_to_start('YCSB', node_count):


def configure_db_instances():
    commands = fabric_variable_bypass['pre-reboot-settings']
    with settings(connection_attempts=100, timeout=5):
        for command in commands:
            sudo(command)


def wait_for_tagged_hosts_to_start(tag, count):
    while len(get_external_ips(tag, False).split()) < int(count):
        print "Waiting for %s hosts to start. Currently %s" % (count, len(get_external_ips(tag, False).split()))
        time.sleep(1)

    # Test the ssh connection with test connection with retries
    execute(
        test_connection_with_wait,
        hosts=get_external_ips(tag, False).split()
    )


def test_connection_with_wait():
    with settings(connection_attempts=100, timeout=5):
        run("echo 'testing connection'")


def reboot_instances(tag):
    ids = get_instance_ids_for_tag(tag).split()
    local("aws ec2 reboot-instances --instance-ids %s" % " ".join(ids))


def amazon_start(db):
    database = get_db(db)
    start_db_instances(database)
    start_ycsb_instances()


def amazon_terminate():
    out = Popen(["%sec2terminate" % dir], stdout=PIPE).communicate()[0]
    print out


def amazon_status():
    out = Popen(["%sec2status" % dir], stdout=PIPE).communicate()[0]
    print out


def test(c):
    wait_for_tagged_hosts_to_start('DB', c)








