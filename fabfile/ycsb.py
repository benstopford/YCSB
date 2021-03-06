import re, os, tempfile


from fabric.api import *
from fabric.colors import green, blue, red
from conf import workloads
from fabfile.helpers import get_db, get_workload, _at, get_outfilename, base_time, almost_nothing, get_properties, \
    determine_file
from conf.hosts import addresses, running_ycsb_node_count
from util.print_utils import log
from fabfile.amazonctl.amazon_helper import record_stage, stage_complete


def _ycsbloadcmd(database, clientno, timestamp, target=None):
    totalclients = running_ycsb_node_count()
    cmd = workloads.root + '/bin/ycsb load %s -s' % database['command']
    for (key, value) in get_properties(database).items():
        if key == 'operationcount':
            cmd += ' -p %s=%s' % (key, value / totalclients)
        elif key == 'insertcount':
            insertcount = workloads.conf['insertcount'] / totalclients
            cmd += ' -p insertcount=%s' % insertcount
        else:
            cmd += ' -p %s=%s' % (key, value)

    starting_point = 0
    if 'insertstart' in workloads.conf.keys():
        starting_point = workloads.conf['insertstart']
    insertstart = starting_point + insertcount * clientno
    cmd += ' -p insertstart=%s' % insertstart

    # record count is the keyspace used for reads. If it has not been set just default it to the insert count
    if 'recordcount' not in workloads.conf.keys():
        cmd += ' -p recordcount=%s' % workloads.conf['insertcount']

    if target is not None:
        cmd += ' -target %s' % str(target)
    outfile = get_outfilename(database['name'], 'load', 'out', timestamp)
    errfile = get_outfilename(database['name'], 'load', 'err', timestamp)
    cmd += ' > %s/%s' % (database['home'], outfile)
    cmd += ' 2> %s/%s' % (database['home'], errfile)
    return cmd


def _ycsbdbinitcommand(database):
    print 'initialising tables etc for '+database['name']
    cmd = 'bin/ycsb init %s -s' % database['command']
    cmd += ' -p hosts=%s' % addresses()['db_public_ip'][0]
    for (key, value) in get_properties(database).items():
        if key != 'hosts':
            cmd += ' -p %s=%s' % (key, value)

    return cmd


def _ycsbruncmd(database, workload, timestamp, target=None):
    totalclients = running_ycsb_node_count()
    cmd = workloads.root + '/bin/ycsb'
    cmd += ' run %s -s' % database['command']
    for file in workload['propertyfiles']:
        cmd += ' -P %s' % file
    for (key, value) in get_properties(database, workload).items():
        if key == 'operationcount':
            cmd += ' -p %s=%s' % (key, value / totalclients)
        else:
            cmd += ' -p %s=%s' % (key, value)
    if target is not None:
        cmd += ' -target %s' % str(target)
    outfile = get_outfilename(database['name'], workload['name'], 'out', timestamp, target)
    errfile = get_outfilename(database['name'], workload['name'], 'err', timestamp, target)
    cmd += ' > %s/%s' % (database['home'], outfile)
    cmd += ' 2> %s/%s' % (database['home'], errfile)
    return cmd


def _client_no():
    return addresses()['ycsb_public_ip'].index(env.host)

def _intialise_tables(db):
    database = get_db(db)
    local(_ycsbdbinitcommand(database))

@parallel
def _do_load(db, target=None):
    log("Starting ycsb load phase [%s]" %env.host)
    timestamp = base_time()
    print green(timestamp, bold=True)
    clientno = _client_no()
    database = get_db(db)
    with cd(database['home']):
        if target is not None:
            part = int(target) / running_ycsb_node_count()
            run(_at(_ycsbloadcmd(database, clientno, timestamp, part), timestamp))
        else:
            run(_at(_ycsbloadcmd(database, clientno, timestamp), timestamp))


def load(db, target=None):
    """Starts loading of data to the database"""
    _intialise_tables(db)
    execute(
        _do_load,
        db,
        target,
        hosts=addresses()['ycsb_public_ip']
    )


def do_workload(db, workload, target=None):
    log('Starting workload %s on [%s]'%(workload, env.host))
    timestamp = base_time()
    print green(timestamp, bold=True)
    database = get_db(db)
    load = get_workload(workload)
    with cd(database['home']):
        if target is not None:
            part = int(target) / running_ycsb_node_count()
            run(_at(_ycsbruncmd(database, load, timestamp, part), timestamp))
        else:
            run(_at(_ycsbruncmd(database, load, timestamp), timestamp))


def run_workload(db, workload, target=None):
    """Starts running of the workload"""
    execute(
        do_workload,
        db,
        workload,
        target,
        hosts=addresses()['ycsb_public_ip']
    )


def _status(db):
    with almost_nothing():
        database = get_db(db)
        dir_name = database['home']
        with cd(database['home']):
            # we need to provide the info for the latest modified
            # file, therefore we need to check the times
            # recursively list all err files and modification times
            lines = run('find . -name "*.err" -printf "%p %T@\n"').split('\r\n')

            def extract(line):
                (f, t) = line.split(' ')
                (d, f) = os.path.split(f)
                return (d, f, float(t))

            def order(t):
                return -t[2]

            if lines and not (len(lines) == 1 and not lines[0]):
                files = sorted(map(extract, lines), key=order)
                (d, f, t) = files[0]
                dir_name = os.path.normpath(os.path.join(database['home'], d))
        with cd(dir_name):
            ls_out = run('ls --format=single-column --sort=t *.lock')
            msg = green('free') if 'cannot access' in ls_out else red('locked')
            print blue('Lock:', bold=True), msg
            print blue('Scheduled:', bold=True)
            # print run('tail -n 2 /var/spool/cron/atjobs/*')
            print sudo('atq')
            print blue('Running:', bold=True)
            print run('ps -f -C java')
            # print run('ps aux | grep python')
            # sort the output of ls by date, the first entry should be the *.err needed
            ls_out = run('ls --format=single-column --sort=t *.err')
            if 'cannot access' in ls_out:
                logfile = '<no any *.err files>'
                tail = ''
            else:
                ls = ls_out.split("\r\n")
                logfile = ls[0]
                tail = run('tail %s' % logfile)
            print blue('Dir:', bold=True), green(dir_name, bold=True)
            print blue('Log:', bold=True), green(logfile, bold=True)
            print tail
            # print blue('List:', bold = True)
            # ls_out = run('ls --format=single-column --sort=t')
            # print ls_out
            print


def status(db):
    """ Shows status of the currently running YCSBs """
    execute(
        _status,
        db,
        hosts=addresses()['ycsb_public_ip']
    )


@parallel
def do_get_log(db, regex='.*', do=True):
    database = get_db(db)
    with almost_nothing():
        cn = _client_no() + 1
        with cd(database['home']):
            (f0, is_dir) = determine_file(regex)
            print blue('Filename at c%s: ' % cn, bold=True), green(f0, bold=True)
        # now do the processing, if enabled
        # If do is presented, then do is str. bool(str) = True if str is not empty
        # May be we should process str as bool?
        if do:
            with cd(database['home']):
                if is_dir:
                    tempdir_local = '%s/c%s' % (tempfile.gettempdir(), cn)
                    dir_local = './%s-c%s' % (f0, cn)
                    bz2_remote = '%s-c%s-dir.bz2' % (f0, cn)
                    bz2_full_local = '%s/%s-dir.bz2' % (tempdir_local, f0)
                    # packing
                    print blue('c%s packing ...' % cn)
                    #run('tar -jcvf %s %s' % (bz2_remote, f0))
                    #To ignore huge err files.
                    run('tar -jcvf %s %s/*.out' % (bz2_remote, f0))
                    # download them
                    print blue('c%s transferring to %s...' % (cn, tempdir_local))
                    get(bz2_remote, bz2_full_local)
                    # the files are here, remove remote bz2
                    run('rm -f %s' % bz2_remote)
                    # unpacking to temp dir
                    print blue('c%s unpacking ...' % cn)
                    local('tar -xvf %s -C %s' % (bz2_full_local, tempdir_local))
                    print blue('c%s moving to current dir %s' % (cn, tempdir_local))
                    # remove the old version of the dir
                    # TODO maybe use versioning?
                    local('rm -rf %s' % dir_local)
                    local('mkdir -p %s' % dir_local)
                    local('mv %s/%s/* %s' % (tempdir_local, f0, dir_local))
                    # additional step - rename all the files
                    # *.err and *.out in the folder
                    rename_cmd = 'for i in ./%s/*.*; do  ' \
                                 ' ext="${i##*.}"      ; ' \
                                 ' fil="${i%%.*}-c%s"  ; ' \
                                 ' mv "$i" "$fil.$ext" ; ' \
                                 'done' % (dir_local, cn)
                    local(rename_cmd)
                    local('rm -rf %s' % tempdir_local)
                else:
                    tempdir_local = '%s/c%s' % (tempfile.gettempdir(), cn)
                    bz2err_remote = '%s-c%s-err.bz2' % (f0, cn)
                    bz2out_remote = '%s-c%s-out.bz2' % (f0, cn)
                    bz2err_full_local = '%s/%s-err.bz2' % (tempdir_local, f0)
                    bz2out_full_local = '%s/%s-out.bz2' % (tempdir_local, f0)
                    # packing
                    print blue('c%s packing ...' % cn)
                    run('tar -jcvf %s %s.err' % (bz2err_remote, f0))
                    run('tar -jcvf %s %s.out' % (bz2out_remote, f0))
                    # download them
                    print blue('c%s transferring to %s...' % (cn, tempdir_local))
                    get(bz2err_remote, bz2err_full_local)
                    get(bz2out_remote, bz2out_full_local)
                    # the files are here, remove remote bz2
                    run('rm -f %s' % bz2err_remote)
                    run('rm -f %s' % bz2out_remote)
                    # unpacking to temp dir
                    print blue('c%s unpacking ...' % cn)
                    local('tar -xvf %s -C %s' % (bz2err_full_local, tempdir_local))
                    local('tar -xvf %s -C %s' % (bz2out_full_local, tempdir_local))
                    # unpacked ok, remove local bz2
                    #local('rm -f %s' % bz2err_full_local)
                    #local('rm -f %s' % bz2out_full_local)
                    print blue('c%s moving to current dir %s' % (cn, tempdir_local))
                    local('mv %s/%s.err ./logs/%s-c%s.err' % (tempdir_local, f0, f0, cn))
                    local('mv %s/%s.out ./logs/%s-c%s.out' % (tempdir_local, f0, f0, cn))
                    local('rm -rf %s' % tempdir_local)


def get_log(db, regex='.*', do=True):
    """ Download *.err and *.out logs satisfying the regex to be transferred
    OR transfer all logs in the batch dir
    """
    execute(
        do_get_log,
        db,
        regex,
        do,
        hosts=addresses()['ycsb_public_ip']
    )


@parallel
def do_kill():
    with settings(warn_only=True):
        run('ps -f -C java')
        run('sudo killall java')


def kill():
    """Kills YCSB processes"""
    execute(
        do_kill,
        hosts=addresses()['ycsb_public_ip']
    )

@parallel
def do_clean():
    run('rm -rf ~/*.err')
    run('rm -rf ~/*.out')


def clean_logs():
    """Removes all logs"""
    do_clean
    execute(
        do_clean,
        hosts=addresses()['ycsb_public_ip']
    )

@runs_once
def _build_and_upload():
    local('mvn clean package')
    put('distribution/target/ycsb-0.1.4.tar.gz', '~/ycsb.tar.gz')
    print ""

@parallel
def pull_from_master(master):
    run('scp -o StrictHostKeyChecking=no -i %s %s:ycsb.tar.gz .' % (env.key_filename, master))
    with cd('/opt'):
        run('sudo ln -sf ycsb-0.1.4 ycsb')
        run('sudo rm -rf ycsb-0.1.4')
        run('sudo tar xzvf ~/ycsb.tar.gz')


def _deploy():
    log('Starting ycsb deploy [%s]'%env.host)
    upload_key()
    _build_and_upload()
    client1 = addresses()['ycsb_private_ip'][0]
    print "pulling jars from each YCSB node from the distribution proxy:%s" % client1
    pull_from_master(client1)


def deploy(force=False):
    """Builds and deploy\s YCSB to the clients. the Force argument forces redeployment"""
    force=bool(force)

    if force or not stage_complete('YCSB', 'ycsb-deploy'):
        execute(
            _deploy,
            hosts=addresses()['ycsb_public_ip']
        )

    record_stage('YCSB','ycsb-deploy')

def upload_key():
    run('sudo rm -f %s' % env.key_filename)
    put(env.key_filename, '~/%s' % env.key_filename)
    run('sudo chmod 400 %s' % env.key_filename)


@parallel
def _test():
    run('sleep 10')
    run('echo "testing..."')


@parallel
def _test2():
    run('starting test2')
    run('sleep 10')
    run('echo "testing..."')


def test():
    execute(
        _test,
        hosts=addresses()['db_public_ip'] + addresses()['man_public_ip'] + addresses()['ycsb_public_ip']
    )
    execute(
        _test2,
        hosts=addresses()['db_public_ip'] + addresses()['man_public_ip'] + addresses()['ycsb_public_ip']
    )
    print 'post parallel runs now'





