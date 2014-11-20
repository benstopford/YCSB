from fabric.api import *

@roles('db_public_ip')
@parallel
def aerospike_start():
    """Starts aerospike on servers"""
    with settings(warn_only=True):
        run('/etc/init.d/citrusleaf start')

@roles('db_public_ip')
@parallel
def aerospike_stop():
    """Stops aerospike on servers"""
    with settings(warn_only=True):
        run('/etc/init.d/citrusleaf stop')

