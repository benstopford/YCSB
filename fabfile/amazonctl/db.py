import subprocess
import fabfile.conf.hosts
from fabric.api import *
from fabfile.amazonctl.amazon_helper import *
from fabfile.helpers import get_db
from fabfile.amazonctl.amazon_ip import *
from fabfile.conf.machine_config import core_machine_settings
from fabfile.util.print_utils import emphasis

def db_up(db):
    emphasis('db_up')

    actions = get_db(db)['actions'];
    print emphasis('Installing %s' % db)
    actions['install']()

    print emphasis('Starting %s' % db)
    actions['run']()

def db_down(db):
    emphasis('db_down')
    get_db(db)['actions']['stop']();

def test():
    get_db('mongodb')['actions']['run']()