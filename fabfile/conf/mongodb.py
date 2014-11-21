from fabric.api import *
import time


def install_package():
    file = "/etc/yum.repos.d/mongodb.repo"
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


def start_mongod():
    sudo('rm /var/log/mongodb/mongod.log')
    sudo('sudo service mongod stop')
    sudo('sudo service mongod start')
    sudo('sudo chmod 777 /var/log/mongodb')
    sudo('sudo chmod 777 /var/log/mongodb/mongod.log')
    out = run('cat  /var/log/mongodb/mongod.log | grep "waiting for connections on port" | wc -l')
    if out != "1":
        raise Exception('Mongo failed to start')

    wait_for_connection('localhost:27017')


def start_mongo_config_server():
    sudo('mkdir -p /data/configdb')
    sudo('chmod 777 /data/configdb')
    sudo('killall -q mongod',warn_only=True)
    sudo('echo "mongod --configsvr --dbpath /data/configdb --port 27027 >/var/log/mongodb/mongo-cfg.log 2>/var/log/mongodb/mongo-cfgerr.log" | at now')

    wait_for_connection('localhost:27027')

def start_mongos():
    config_server = env.roledefs['man_public_ip'][0]
    sudo("killall -q mongos",warn_only=True)
    sudo('echo "mongos --configdb %s:27027 --port 27028 >/var/log/mongodb/mongos.log 2>/var/log/mongodb/mongos-err.log" | at now' % config_server)

    wait_for_connection('localhost:27028')

def wait_for_connection(url):
    while 'MongoDB shell version' not in run('mongo %s --eval "version()"' % url):
        time.sleep(1)
        print 'Waiting for Mongo node %s to open connections' % url

    print 'Connected to mongo on '+env.host_string


def configure_sharding():
    mongods = env.roledefs['db_private_ip']

    for mongod in mongods:
        run('mongo localhost:27028/ycsb --eval "sh.addShard( \'%s:27017\')"' % mongod)

    run('mongo localhost:27028/ycsb --eval "sh.enableSharding(\'ycsb\')"')
    run('mongo localhost:27028/ycsb --eval "sh.shardCollection(\'ycsb.usertable\', { \'_id\': \'hashed\' })"')
    run('mongo localhost:27028/ycsb --eval "db.usertable.remove({})"')


def install():
    """This template method allows you to configure your server - use the various roles defined to configure different nodes"""

    mongo_nodes = env.roledefs['db_public_ip']
    config_server = env.roledefs['man_public_ip']
    all = mongo_nodes + config_server

    print 'Installing & Starting Mongod/Mongos on hosts: %s' % mongo_nodes
    print 'Installing & Starting Config Server on hosts: %s' % config_server

    execute(
        install_package,
        hosts=all
    )

    execute(
        start_mongo_config_server,
        hosts=config_server
    )
    execute(
        start_mongod,
        hosts=mongo_nodes
    )

    execute(
        start_mongos,
        hosts=mongo_nodes
    )

    execute(
        configure_sharding,
        hosts=mongo_nodes[0]
    )


    print '********Mongo is installed and running********'