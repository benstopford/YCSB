from fabric.api import *
from fabfile.amazonctl.amazon_helper import *
from fabfile.helpers import get_db
from fabfile.amazonctl.amazon_ip import *
from fabfile.util.print_utils import emphasis, log
import amazon_helper

def db_up(db, force=False):
    force = bool(force)
    log('db_up: '+db)

    actions = get_db(db)['actions']

    if force or not amazon_helper.stage_complete("DB","db-install"):
        actions['install']()
        log('Installing %s' % db)
        amazon_helper.record_stage("DB","db-install")
    else :
        print 'Skipping install of '+db

    log('Starting %s' % db)
    actions['run']()

def db_down(db):
    log('db_down: '+db)
    get_db(db)['actions']['stop']()

def test():
    get_db('mongodb')['actions']['run']()