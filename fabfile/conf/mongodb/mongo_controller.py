from fabric.api import *
import time
from fabfile.util.print_utils import emphasis
from shutil import *
from fabfile.util.file_utils import replace_in_file, append_line_to_file
import tempfile
import os
from fabfile.conf.hosts import use_instance_store, instance_store_root_dir
from fabfile.conf.hosts import addresses, running_db_node_count, running_ycsb_node_count


instance_store_mondod_db_path = instance_store_root_dir+'/data'

#leave synchronous else fabric reuses the same temp file
def change_mongod_conf():
    print 'overriding bind_ip'
    conf = get(remote_path='/etc/mongod.conf', local_path=tempfile.gettempdir())
    for f in conf:
        # comment out bind_ip default (to allow remote access)
        replace_in_file(f, 'bind_ip=127.0.0.1', '#bind_ip=127.0.0.1')
        if use_instance_store:
            dbpath = instance_store_mondod_db_path+'/mongod'
            sudo('mkdir -p '+dbpath)
            sudo('chmod 777 '+dbpath)
            #change the database file to the correct directory
            replace_in_file(f, 'dbpath=/var/lib/mongo', 'dbpath=' + dbpath)
        append_line_to_file(f, 'quiet=true')
        append_line_to_file(f, 'journal=true')
        put(local_path=f, remote_path='/etc/mongod.conf', use_sudo=True)
        os.remove(f)

@parallel
def start_mongod():

    with settings(warn_only=True):
        sudo('rm /var/log/mongodb/mongod.log')
        sudo('sudo service mongod stop')

    sudo('sudo service mongod start')
    sudo('sudo chmod 777 /var/log/mongodb')
    sudo('sudo chmod 777 /var/log/mongodb/mongod.log')

    # Check 5 times as mongo doesn't always start instantly
    out = ""
    for i in range(5):
        out = run('cat  /var/log/mongodb/mongod.log | grep "waiting for connections on port" | wc -l')
        if out == "1":
            continue

    if out != "1":
        run('tail  /var/log/mongodb/mongod.log')
        raise Exception('Mongo failed to start')

    wait_for_connection('localhost:27017')
    print 'succeeded in connecting to mongod'


def start_mongo_config_server():
    sudo('killall -q mongod', warn_only=True)

    dbpath = instance_store_mondod_db_path + '/configdb' if use_instance_store else '/data/configdb'

    sudo('rm -rf %s'%dbpath)
    sudo('mkdir -p %s'%dbpath)
    sudo('chmod 777 %s'%dbpath)

    sudo(
        'echo "mongod --configsvr --dbpath ' + dbpath + ' --port 27027 >/var/log/mongodb/mongo-cfg.log 2>/var/log/mongodb/mongo-cfgerr.log" | at now')

    wait_for_connection('localhost:27027')
    print 'succeeded in connecting to mongod config server'


def start_mongos():
    config_server = addresses()['man_public_ip'][0]
    sudo("killall -q mongos", warn_only=True)
    sudo(
        'echo "mongos --configdb %s:27027 --port 27028 >/var/log/mongodb/mongos.log 2>/var/log/mongodb/mongos-err.log" | at now' % config_server)

    wait_for_connection('localhost:27028')
    print 'succeeded in connecting to mongos'


def wait_for_connection(url):
    with settings(warn_only=True, quiet=True):
        while 'Failed to connect to ' in run('mongo %s --eval "version()"' % url):
            time.sleep(1)
            print 'Waiting for Mongo node %s to open connections' % url

    print '****Succeeded connecting to mongo on %s****' % env.host_string


def run_mongo_shell(url, command, acceptable_error='', check_return_code=True):
    command_no_check = 'mongo %s --eval "%s"' % (url, command)
    command_return_code = 'mongo %s --eval "%s[\'ok\']"' % (url, command)
    command_error_desc = 'mongo %s --eval "%s[\'errmsg\']"' % (url, command)

    if (check_return_code):
        ret = run(command_return_code).split('\n')

        print "mongo shell returned %s" % ret
        if ret[-1] == '' and ret[-1] == "1":
            print 'Command succeeded: %s' % ret
        else:
            error = run(command_error_desc).split('\n')[-1]
            if len(acceptable_error) > 0 and acceptable_error in error:
                print 'WARNING: shell command returned with a permissible error: %s' % error
            else:
                print 'Exception running mongo shell command:'
                raise Exception('Mongo shell command failed:\ncmd="%s"\nerror="%s"' % (command, error))
    else:
        run(command_no_check)


def configure_sharding():
    mongods = addresses()['db_private_ip']

    url = 'localhost:27028/ycsb'
    for mongod in mongods:
        run_mongo_shell(url, 'sh.addShard(\'%s:27017\')' % mongod, acceptable_error='host already used')

    run_mongo_shell(url, 'sh.enableSharding(\'ycsb\')', acceptable_error='already enabled')
    run_mongo_shell(url, 'sh.shardCollection(\'ycsb.usertable\', { \'_id\': \'hashed\' })',
                    acceptable_error='already sharded')
    run_mongo_shell(url, 'db.usertable.remove({})', check_return_code=False)


@parallel
def stop_mongos():
    sudo("killall -q mongos", warn_only=True)

def clear_directory(dir):
    sudo('rm -rf '+dir)
    sudo('mkdir -p '+dir)
    sudo('chmod 777 '+dir)

@parallel
def stop_mongod():
    sudo('sudo service mongod stop')
    clear_directory(instance_store_mondod_db_path)
    clear_directory('/var/lib/mongo')


def stop_config_server():
    sudo('killall -q mongod', warn_only=True)
    clear_directory(instance_store_mondod_db_path)
    clear_directory('/data/configdb')



def start():
    """Runs MongoDB"""

    mongo_nodes = addresses()['db_public_ip']
    config_server = addresses()['man_public_ip']

    print 'stopping mongo first...'
    stop()

    print 'Installing & Starting Mongod/Mongos on hosts: %s' % mongo_nodes
    print 'Installing & Starting Config Server on hosts: %s' % config_server

    print emphasis('changing configuration')
    execute(
        change_mongod_conf,
        hosts=mongo_nodes
    )

    print emphasis('starting config server')
    execute(
        start_mongo_config_server,
        hosts=config_server
    )

    print emphasis('starting mongod')
    execute(
        start_mongod,
        hosts=mongo_nodes
    )

    print emphasis('starting mongos')
    execute(
        start_mongos,
        hosts=mongo_nodes
    )

    print emphasis('configuring sharding')
    execute(
        configure_sharding,
        hosts=mongo_nodes[0]
    )

    print '********Mongo is running********'


def stop():
    """Stops Mongodb"""
    mongo_nodes = addresses()['db_public_ip']
    config_server = addresses()['man_public_ip']
    execute(
        stop_mongod,
        hosts=mongo_nodes
    )
    execute(
        stop_mongos,
        hosts=mongo_nodes
    )
    execute(
        stop_config_server,
        hosts=config_server
    )


