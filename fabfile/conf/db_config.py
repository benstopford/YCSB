from fabric.api import env
import cassandra.cassandra_controller
import cassandra.cassandra_installer
import mongodb.mongo_installer
import mongodb.mongo_controller
import hosts


def dbs():
    return {
        'cassandra': {
            'name': 'cassandra',
            'home': '/home/%s' % hosts.ycsb_ec2_user,
            'logs': '/var/log/cassandra/system.log',
            'command': 'cassandra-cql',
            'has_management_node': False,
            'properties': {
                'hosts': ','.join(hosts.addresses()['db_public_ip']),
                'cassandra.readconsistencylevel': 'ONE',
                'cassandra.writeconsistencylevel': 'ONE',  # ALL-sync/ONE-async
            },
            'actions': {
                'install': cassandra.cassandra_installer.install,
                'run': cassandra.cassandra_controller.start,
                'stop': cassandra.cassandra_controller.stop
            },
            'permissablerunerrors': ['log4j:WARN']
        },

        'mongodb': {
            'name': 'mongodb',
            'home': '/home/%s' % hosts.ycsb_ec2_user,
            'command': 'mongodb',
            'has_management_node': True,
            'properties': {
                'mongodb.url': ",".join([w + ":27028" for w in hosts.addresses()['db_private_ip']]),
                'mongodb.database': 'ycsb',
                'mongodb.writeConcern': 'normal',
                'mongodb.readPreference': 'primaryPreferred',
            },
            'actions': {
                'install': mongodb.mongo_installer.install,
                'run': mongodb.mongo_controller.start,
                'stop': mongodb.mongo_controller.stop
            }
        },

        'basic': {  # fake database
                    'name': 'basic',
                    'home': '/home/%s' % hosts.ycsb_ec2_user,
                    'has_management_node': False,
                    'command': 'basic',
                    'properties': {
                        'basicdb.verbose': 'false',
                        'hosts': ','.join(hosts.addresses()['db_public_ip']),
                        'basic.url': ",".join([w + ":27028" for w in hosts.addresses()['db_private_ip']]),
                    }
        }

    }

