from fabric.api import *
from shutil import *
import os
import time
from fabfile.conf.hosts import addresses, running_db_node_count, running_ycsb_node_count


def wait_to_cluster():
    expected_node_count = running_db_node_count()
    count = 0

    while 1:
        out = run('nodetool status | grep UN | wc -l', quiet=True)
        if len(out) < 5 and int(out) == expected_node_count:
            print 'Cassandra cluster formed with %s nodes' % int(out)
            break
        count += 1; time.sleep(1); print 'waiting for Casandra to cluster'
        if count == 20:
            out = run('nodetool status')
            print out
            raise Exception("Cassandra did not cluster! ...")

@parallel
def start_cassandra():
    _stop()
    sudo("rm -rf /var/lib/cassandra/*")
    sudo('service cassandra start')


def start():
    print 'Starting Cassandra on hosts: %s' % addresses()['db_public_ip']
    execute(
        start_cassandra,
        hosts=addresses()['db_public_ip']
    )
    execute(
        wait_to_cluster,
        hosts=addresses()['db_public_ip'][0]
    )
    print '********Cassandra is running and clustered********'


@parallel
def _stop():
    sudo("service cassandra stop")


def stop():
    execute(
        _stop,
        hosts=addresses()['db_public_ip']
    )



