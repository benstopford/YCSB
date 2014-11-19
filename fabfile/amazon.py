
from fabric.api import env, hosts, roles, run,settings, execute, sudo, local
import subprocess
from fabfile.helpers import get_db
# from fabric.api import *
from conf.hosts import generate_roledefs
from amazon_ip import *
import time


dir = "fabfile/amazonctl/"



def start_db_instances(database):
    """Starts defined database instances if they are not already running"""

    node_count = int(env.db_node_count)
    current = len(get_external_ips('DB',False).split())

    if database['has_management_node'] in 'True':
        node_count += 1

    if current >= node_count:
        print "Not starting new database nodes as there are already %s running." % current
        return

    if node_count > current > 0:
        node_count = node_count - current
        print "There are already %s nodes running so we will only start %s additional ones" % (current, node_count)

    command = ["aws", "ec2", "run-instances",
               "--count=" + `node_count`,
               "--instance-type=" + env.db_instance_type,
               "--key-name=datalabs-dsc1",
               "--security-groups=my-eu-sec-group"
    ]

    for key, value in database['ec2_config'].iteritems():
        command.append(key + "=" + value)

    print command
    out = subprocess.check_output(command)

    #Tag the instances we created - TODO: replace with regex
    final = ""
    lines = out.split("\n")
    for line in lines:
        if line.startswith("INSTANCES"):
            for word in line.split("\t"):
                if(word.startswith("i-")):
                    subprocess.call(["%sec2tag2" % dir, word, "DB"])
                    final = word

    # Tag the final nods as the management node
    if database['has_management_node'] in 'True':
        subprocess.call(["%sec2tag2" % dir, final, "DB_MAN"])

    wait_for_tagged_hosts_to_start('DB',node_count)

    #Add machine specific config such as ulimits
    execute(
        configure_db_instances,
        hosts=generate_roledefs()['server']
    )

    reboot_instances('DB')

    wait_for_tagged_hosts_to_start('DB',node_count)



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
               "--count=" + node_count,
               "--image-id=" + env.ycsb_ami,
               "--instance-type=" + env.ycsb_instance_type,
               "--key-name=datalabs-dsc1",
               "--security-groups=my-eu-sec-group"
    ]
    print command

    out = subprocess.check_output(command)

    #Tag the instances we just created
    lines = out.split("\n")
    for line in lines:
        if line.startswith("INSTANCES"):
            for word in line.split("\t"):
                if(word.startswith("i-")):
                    subprocess.call(["%sec2tag2" % dir, word, "YCSB"])

def configure_db_instances():
    with settings(connection_attempts=100, timeout=5):
        sudo("chmod 777 /etc/security/limits.conf")
        sudo('if ! grep -q "\* soft nofile 20000" /etc/security/limits.conf; then echo "* soft nofile 20000" >> /etc/security/limits.conf; fi')
        sudo('if ! grep -q "\* hard nofile 20000" /etc/security/limits.conf; then echo "* hard nofile 20000" >> /etc/security/limits.conf; fi')
        sudo("chmod 644 /etc/security/limits.conf")


def wait_for_tagged_hosts_to_start(tag, count):
    while len(get_external_ips(tag, False).split()) < int(count):
        print "Waiting for %s hosts to start. Currently %s" % (count, len(get_external_ips(tag,False).split()))
        time.sleep(1)

    #Test the ssh connection with test connection with retries
    execute(
        test_connection_with_wait,
        hosts=get_external_ips(tag,False).split()
    )

def test_connection_with_wait():
    with settings(connection_attempts=100, timeout=5):
        run("echo 'testing connection'")

def reboot_instances(tag):
    ids = get_instance_ids_for_tag(tag).split()
    local("aws ec2 reboot-instances --instance-ids %s" % " ".join(ids))

def amazon_start(db):
    start_db_instances(get_db(db))
    start_ycsb_instances()

def amazon_terminate():
    out = Popen(["%sec2terminate" % dir], stdout=PIPE).communicate()[0]
    print out


def amazon_status():
    out = Popen(["%sec2status" % dir], stdout=PIPE).communicate()[0]
    print out


def test(c):
    wait_for_tagged_hosts_to_start('DB',c)








