from fabric.api import *
from shutil import *
import os
from fabfile.conf.hosts import use_instance_store, instance_store_root_dir


def install_cassandra():
    sudo("rm -f /etc/yum.repos.d/datastax.repo")
    sudo("touch /etc/yum.repos.d/datastax.repo")
    sudo("chmod 777 /etc/yum.repos.d/datastax.repo")
    sudo('echo "[datastax] \n'
         'name = DataStax Repo for Apache Cassandra\n'
         'baseurl = http://rpm.datastax.com/community\n'
         'enabled = 1\n'
         'gpgcheck = 0" '
         '> /etc/yum.repos.d/datastax.repo')
    sudo("chmod 644 /etc/yum.repos.d/datastax.repo")
    sudo('yum -y install dsc21')
    sudo('chmod 777 /var/lib/cassandra')


def install_java():
    java_version = run("java -version")
    if "Java(TM) SE Runtime Environment (build 1.7.0_25-b15)" not in java_version:
        print 'Installing java on %s' % env.host_string
        run('wget --no-cookies --header "Cookie: gpw_e24=xxx;oraclelicense=accept-securebackup-cookie; " '
            'http://download.oracle.com/otn-pub/java/jdk/7u25-b15/jdk-7u25-linux-x64.rpm')
        sudo("rpm -i jdk-7u25-linux-x64.rpm")
        sudo("sudo alternatives --install /usr/bin/java java /usr/java/default/bin/java 20000")
        sudo("export JAVA_HOME=/usr/java/default")
        print '*******************Java was upgraded to:*******************'
        run("java -version")
    else:
        print 'Java is correct, proceeding\n'


def prepare_directories():
    _commit_log_dir = (instance_store_root_dir + '/commitlog')
    _data_dir = (instance_store_root_dir + '/data')
    if (use_instance_store):
        sudo('mkdir -p %s' % _commit_log_dir)
        sudo('chmod 777 %s' % _commit_log_dir)
        sudo('mkdir -p %s' % _data_dir)
        sudo('chmod 777 %s' % _data_dir)
    return _commit_log_dir, _data_dir


def make_substitutions(base, yaml):
    seed = env.roledefs['db_private_ip'][0]
    index = env.roledefs['db_public_ip'].index(env.host_string)
    host_internal_ip = env.roledefs['db_private_ip'][index]

    _commit_log_dir, _data_dir = prepare_directories()

    with open(yaml, "wt") as fout:
        with open(base, "rt") as fin:
            for line in fin:
                line = line.replace('seeds: "127.0.0.1"', 'seeds: "%s"' % seed)
                line = line.replace('listen_address: localhost', 'listen_address: %s' % host_internal_ip)
                line = line.replace('# broadcast_rpc_address: 1.2.3.4', 'broadcast_rpc_address: %s' % host_internal_ip)
                if use_instance_store:

                    line = line.replace('commitlog_directory: /var/lib/cassandra/commitlog',
                                        'commitlog_directory: %s' % _commit_log_dir)

                    line = line.replace(' - /var/lib/cassandra/data',
                                        ' - /%s' % _data_dir)

                fout.write(line)
        fout.write("\nauto_bootstrap: false")


def make_substitutions_and_push_yaml():
    yaml = "fabfile/conf/cassandra/cassandra.yaml"
    base = "fabfile/conf/cassandra/cassandra_raw.yaml"
    if os.path.exists(yaml):
        os.remove(yaml)
    copyfile(base, yaml)

    make_substitutions(base, yaml)

    put(yaml)
    sudo('mv cassandra.yaml  /etc/cassandra/conf/cassandra.yaml')
    copyfile(yaml, yaml + env.host_string)
    os.remove(yaml)


@parallel
def _install():
    sudo("yum -y update")
    install_java()
    install_cassandra()


def _configure():
    make_substitutions_and_push_yaml()

    # fix for node tool in this instalation
    sudo("sudo sed -i 's/jamm-0.2.6.jar/jamm-0.2.8.jar/g'  /usr/share/cassandra/cassandra.in.sh")


def install():
    print 'Installing Cassandra on hosts: %s' % env.roledefs['db_public_ip']

    execute(  # install in parallel
              _install,
              hosts=env.roledefs['db_public_ip']
    )
    execute(
        _configure,
        hosts=env.roledefs['db_public_ip']
    )
    print '********Cassandra is installed********'

