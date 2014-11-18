from conf.hosts import env
from subprocess import *
from fabfile.helpers import get_db
import subprocess

dir = "fabfile/amazonctl/"



def start_db_instances(database):
    db_node_count = int(env.db_node_count)

    if database['has_management_node'] in 'True':
        db_node_count += 1

    command = ["aws", "ec2", "run-instances",
               "--count=" + `db_node_count`,
               "--instance-type=" + env.db_instance_type,
               "--key-name=datalabs-dsc1",
               "--security-groups=my-eu-sec-group"
    ]

    for key, value in database['ec2_config'].iteritems():
        command.append(key + "=" + value)

    print command
    out = subprocess.check_output(command)

    #Tag the instances we created:
    final = ""

    lines = out.split("\n")
    for line in lines:
        if line.startswith("INSTANCES"):
            for word in line.split("\t"):
                if(word.startswith("i-")):
                    subprocess.call(["%sec2tag2" % dir, word, "DB"])
                    final = word

    if database['has_management_node'] in 'True':
        subprocess.call(["%sec2tag2" % dir, final, "DB_MAN"])


def start_ycsb_instances():
    command = ["aws", "ec2", "run-instances",
               "--count=" + env.ycsb_node_count,
               "--image-id=" + env.ycsb_ami,
               "--instance-type=" + env.ycsb_instance_type,
               "--key-name=datalabs-dsc1",
               "--security-groups=my-eu-sec-group"
    ]
    print command

    out = subprocess.check_output(command)

    #tag the instances we just created
    lines = out.split("\n")
    for line in lines:
        if line.startswith("INSTANCES"):
            for word in line.split("\t"):
                if(word.startswith("i-")):
                    subprocess.call(["%sec2tag2" % dir, word, "YCSB"])


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


def test(db):
    database = get_db(db)
    print database['ec2_config']








