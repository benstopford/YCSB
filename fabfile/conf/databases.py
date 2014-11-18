import hosts


databases = {

    'aerospike': {
        'name': 'aerospike',  # name of the database (used to form the logfile name)
        'home': '/run/shm',  # database home, to put logs there
        'command': 'aerospike',  # database name to pass to ycsb command
        'properties': {  #properties to pass to ycsb command as -p name=value
                         'host': 'e1.citrusleaf.local',  #database connection params
                         'port': 3000,
                         'ns': 'test',
                         'set': 'YCSB',
        },
        'status': {
            'hosts': hosts.env.roledefs['server'][0:1],  #hosts on which to run the status command
            'command': '/opt/citrusleaf/bin/clmonitor -e info'  #the status command
        },
        'failover': {
            'files': [],
            'kill_command': '/usr/bin/killall -9 cld',
            'start_command': '/etc/init.d/citrusleaf start',
        },
    },

    'couchbase': {
        'name': 'couchbase',
        'home': '/run/shm',
        'command': 'couchbase',
        'properties': {
            'couchbase.hosts': 'e1.citrusleaf.local,e2.citrusleaf.local,e3.citrusleaf.local,e4.citrusleaf.local',
            'couchbase.bucket': 'test',
            'couchbase.user': '',
            'couchbase.password': '',
            'couchbase.opTimeout': 1000,
            # 'couchbase.failureMode': 'Retry',
            'couchbase.checkOperationStatus': 'true',
        }
    },

    'couchbase2': {
        'name': 'couchbase',
        'home': '/run/shm',
        'command': 'couchbase2',
        'properties': {
            'couchbase.hosts': 'e2.citrusleaf.local,e1.citrusleaf.local,e3.citrusleaf.local,e4.citrusleaf.local',
            'couchbase.bucket': 'test',
            'couchbase.ddocs': '',
            'couchbase.views': '',
            'couchbase.user': '',
            'couchbase.password': '',
            'couchbase.opTimeout': 1000,
            # 'couchbase.failureMode': 'Retry',
            # 'couchbase.persistTo': 'ONE',
            # 'couchbase.replicateTo': 'ONE',
            'couchbase.checkOperationStatus': 'true',
        },
        'failover': {
            'files': ['couchbase_kill.sh', 'couchbase_start.sh'],
            'kill_command': '''\
ssh e1 ~/couchbase_kill.sh; \
sleep 1; \
/opt/couchbase/bin/couchbase-cli failover -c localhost:8091 -u admin -p 123123 --server-failover=192.168.109.168; \
sleep 2; \
/opt/couchbase/bin/couchbase-cli rebalance -c localhost:8091 -u admin -p 123123;''',

            'start_command': '''\
ssh e1 ~/couchbase_start.sh; \
sleep 7; \
/opt/couchbase/bin/couchbase-cli server-add -c localhost:8091 -u admin -p 123123 --server-add=192.168.109.168 --server-add-username=admin --server-add-password=123123; \
sleep 3; \
/opt/couchbase/bin/couchbase-cli rebalance -c localhost:8091 -u admin -p 123123;''',
        }
    },

    'cassandra': {
        'name': 'cassandra',
        'ami': 'ami-8932ccfe',
        'home': '/home/%s' % hosts.env.user,  # logs go here
        'command': 'cassandra-cql',
        'ec2_config': {
            '--image-id': 'ami-a42884d3',
            '--user-data':'"clustername datalabs-cassandra --totalnodes ' + hosts.env.db_node_count + ' --version community"'
        },
        'properties': {
            'hosts': ','.join(hosts.env.roledefs['server']),  # this shouldn't be here - it's dynamic not config
            'cassandra.readconsistencylevel': 'ONE',
            'cassandra.writeconsistencylevel': 'ONE',  # ALL-sync/ONE-async
        },
        'failover': {
            'files': [],
            'kill_command': '/usr/bin/killall -9 java',
            'start_command': '/opt/cassandra/bin/cassandra',
        },
    },

    'mongodb': {
        'name': 'mongodb',
        'home': '/home/%s' % hosts.env.user,
        'command': 'mongodb',
        'has_management_node': 'True',
        'ec2_config': {
            '--image-id': 'ami-5a61d72d',  #test node 'ami-6e7bd919', official mongo base = ami-a42884d3, my ulimit increase ami-5a61d72d
        },

        'start_db_man_script': [
            'sudo mkdir -p /data/configdb',
            'sudo chmod 777 /data/configdb',
            # 'sudo chmod 446 /etc/mongod.conf',
            # 'if ! grep -q "rs1" /etc/mongod.conf; then echo \'replSet = "rs1"\' >> /etc/mongod.conf; fi',
            ' echo "mongod --configsvr --dbpath /data/configdb --port 27027 >config.txt 2>conferr.txt" | at now', # use 'at now' to get around fabric's inability to deal with nohup
        ],
        'start_db_script': [
            # 'echo "sudo sh -c \'ulimit -n 65535 && exec su $LOGNAME\'" > ul.sh',
            # 'echo "exit" >>ul.sh',
            # 'chmod +x ul.sh',
            # './ul.sh',
            # 'ulimit -n',
            'echo "mongos --configdb @MAN:27027 --port 27028 >mongos.txt 2>mongosErr.txt" | at now',
            'sudo service mongod start',
            '#LOOP_DB mongo localhost:27028/ycsb --eval "sh.addShard( \'@DB:27017\')"',
            'mongo localhost:27028/ycsb --eval "sh.enableSharding(\'ycsb\')"',
            'mongo localhost:27028/ycsb --eval "sh.shardCollection(\'ycsb.usertable\', { \'_id\': \'hashed\' })"',
            'mongo localhost:27028/ycsb --eval "db.usertable.remove({})"',
            # 'sudo sh -c "ulimit -n 65535 && exec su $LOGNAME"'

        ],
        'stop_db_script': [
            'sudo killall mongos',
            'sudo killall mongod'
        ],
        'stop_db_man_script': [
            'sudo killall mongod'
        ],

        'properties': {
            'mongodb.url': (
            hosts.env.roledefs['server_private_ip'][0] + ":27028" if len(hosts.env.roledefs['server_private_ip']) > 0 else ""),
            'mongodb.database': 'ycsb',
            'mongodb.writeConcern': 'normal',
            # 'mongodb.writeConcern': 'replicas_safe',
            'mongodb.readPreference': 'primaryPreferred',
        },
        'configdb': 'r5.citrusleaf.local',
        'failover': {
            'files': [],
            'kill_command': '/usr/bin/killall -9 mongod',
            'start_command': '~/mongo_run.sh',
        },
    },

    'hbase': {
        'name': 'hbase',
        'home': '/run/shm',
        'command': 'hbase',
        'properties': {
            'columnfamily': 'family',
        }
    },


    'basic': {  # fake database
                'name': 'basic',
                'home': '/run/shm',
                'command': 'basic',
                'properties': {
                    'basicdb.verbose': 'false',
                }
    },

}

