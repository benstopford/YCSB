import ycsb
import time
import helpers
from fabric.api import *
from helpers import get_db
from util.print_utils import emphasis, log, clear_log
from conf.workloads import conf
from conf.hosts import running_db_node_count, running_ycsb_node_count, host_counts, addresses


def kill_processes():
    if running_ycsb_node_count() > 0:
        execute(
            ycsb.do_kill,
            hosts=addresses()['ycsb_public_ip']
        )

def delete_server_logs():
    if running_ycsb_node_count() > 0:
        execute(
            ycsb.do_clean,
            hosts=addresses()['ycsb_public_ip']
        )

def print_tail(db, lines, filter):
    database = get_db(db)
    with cd(database['home']):
        latest_log = ""
        if len(filter) > 0:
            latest_log = run("ls -ltr | grep %s | awk 'END{print}' | awk {'print $9'};" % filter)
        else:
            latest_log = run("ls -ltr | awk 'END{print}' | awk {'print $9'};")
        if len(latest_log) > 0:
            print run('tail -n-%s %s' % (lines, latest_log))

def tail(lines="70", db='basic', filter=""):
    execute(
        print_tail,
        db,
        lines,
        filter,
        hosts=addresses()['ycsb_public_ip']
    )

def run_status_check(db):
    print emphasis('STATUS CHECK START')
    tail(70, db)
    print emphasis('STATUS CHECK END')

def download_logs(db):
    if not os.path.exists('logs'):
        os.makedirs('logs')
    execute(
        ycsb.do_get_log,
        db,
        hosts=addresses()['ycsb_public_ip']
    )

def await_completion(db):
    while not job_complete(db):
        print 'Polling (15) YCSB log files for completion status'
        time.sleep(15)

def archive_logs():
    with settings(warn_only=True):
        local('./archlogs.sh')

def _ycsb_execution_status(db):
    """ Shows whether the job is:q complete"""
    database = get_db(db)
    with cd(database['home']):
        latest_out_log = run("ls -ltr | grep *.out | awk 'END{print}' | awk {'print $9'};")
        if len(latest_out_log) > 0:

            # Check for errors
            latest_err_log = run("ls -ltr | grep .err | awk 'END{print}' | awk {'print $9'};")

            permissible_errors = ''
            if 'permissablerunerrors' in get_db(db):
                permissible_errors = " ".join(['| grep -v ' + s for s in get_db(db)['permissablerunerrors']])
                print permissible_errors

            lines_in_error_log = run('cat %s %s | grep -v "^ [0-9].*sec" | wc -l' % (latest_err_log, permissible_errors))
            if int(lines_in_error_log) > 8:
                ycsb.do_get_log(db)
                run('tail -n 100 %s ' % latest_err_log)
                raise Exception('Looks like there is something in the error log: %s : %s lines' % (
                    latest_err_log, int(lines_in_error_log)))

            # Check for completion
            complete = run('cat %s | grep "\[OVERALL\]" | wc -l' % latest_out_log)
            run('tail -n-4 %s' % latest_out_log)
            if int(complete) > 0:
                print 'YCSB has completed on %s' % env.host
                return 1
    return 0

def job_complete(db):
    # check one node's status
    first_host = addresses()['ycsb_public_ip'][0]
    success = execute(
        _ycsb_execution_status,
        db,
        hosts=first_host
    )

    # if done check the others
    if success > 0:
        result = execute(
            _ycsb_execution_status,
            db,
            hosts=addresses()['ycsb_public_ip']
        )
        success = sum(result.values()) == running_ycsb_node_count()
        return success

    return 0

def load(db):
    helpers.reset_base_time()
    ycsb.load(db)
    print log('Load has been started: [%s / %s]' % (conf['insertstart'], conf['insertcount']))
    await_completion(db)
    run_status_check(db)
    download_logs(db)
    delete_server_logs()

def run_workload(db, wl):
    helpers.reset_base_time()
    execute(
        ycsb.do_workload,
        db,
        workload=wl,
        hosts=addresses()['ycsb_public_ip']
    )
    print log('Workload %s has been started' % wl)
    await_completion(db)
    run_status_check(db)
    download_logs(db)
    delete_server_logs()


