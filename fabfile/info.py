from fabric.api import *
from conf import hosts as hosts_conf
from fabfile.helpers import get_db

@roles('db_public_ip')
def df():
    """Shows the free disk space on servers"""
    run('df -h')

@hosts(hosts_conf.env.roledefs['db_public_ip'][0])
def db_status(db):
    """Shows the status of the DB"""
    database = get_db(db)
    with settings(hide('stdout'), hosts=database['status']['hosts']):
        print run(database['status']['command'])
