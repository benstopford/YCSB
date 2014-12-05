from fabric.api import env
import cassandra.cassandra_controller
import cassandra.cassandra_installer
import mongodb.mongo_installer
import mongodb.mongo_controller
import fabfile.conf.hosts as hosts


databases = {

    'cassandra': {
        'name': 'cassandra',
        'home': '/home/%s' % hosts.ycsb_ec2_user,
        'command': 'cassandra-cql',
        'has_management_node': False,
        'properties': {
            'hosts': ','.join(env.roledefs['db_public_ip']),
            'cassandra.readconsistencylevel': 'ONE',
            'cassandra.writeconsistencylevel': 'ONE',  # ALL-sync/ONE-async
        },
        'actions': {
            'install': cassandra.cassandra_installer.install,
            'run': cassandra.cassandra_controller.start,
            'stop': cassandra.cassandra_controller.stop
        }
    },

    'mongodb': {
        'name': 'mongodb',
        'home': '/home/%s' % hosts.ycsb_ec2_user,
        'command': 'mongodb',
        'has_management_node': True,
        'properties': {
            'mongodb.url': ",".join([w + ":27028" for w in env.roledefs['db_private_ip']]),
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
                'has_management_node': False,
                'command': 'basic',
                'properties': {
                    'basicdb.verbose': 'false',
                    'hosts': ','.join(env.roledefs['db_public_ip']),
                    'basic.url': ",".join([w + ":27028" for w in env.roledefs['db_private_ip']]),
                }
    }

}

