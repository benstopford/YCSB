import ycsb
from fabric.api import *
from helpers import get_db
import time
from util.print_utils import emphasis
from conf.workloads import data
import helpers
import os


summary_log = "growing_data_group_test_summary.log"

def delete_server_logs():
    execute(
        ycsb.clean_logs,
        hosts=env.roledefs['ycsb_public_ip']
    )


def load(db):
    helpers.reset_base_time()
    execute(
        ycsb.load,
        db,
        hosts=env.roledefs['ycsb_public_ip']
    )
    print log('Load has been started: [%s / %s]' % (data['insertstart'], data['recordcount']))

def run_workload(db, wl):
    helpers.reset_base_time()
    execute(
        ycsb.run_workload,
        db,
        workload=wl,
        hosts=env.roledefs['ycsb_public_ip']
    )
    print log('Workload %s has been started' % wl)


def print_tail(db):
    database = get_db(db)
    with cd(database['home']):
        latest_log = run("ls -ltr | awk 'END{print}' | awk {'print $9'};")
        if len(latest_log) > 0:
            print run('tail -n-70 %s' % latest_log)


def run_status_check(db):
    print log('STATUS CHECK START')
    execute(
        print_tail,
        db,
        hosts=env.roledefs['ycsb_public_ip']
    )
    print log('STATUS CHECK END')


def download_logs(db):
    execute(
        ycsb.get_log,
        db,
        hosts=env.roledefs['ycsb_public_ip']
    )


def kill_processes():
    execute(
        ycsb.kill,
        hosts=env.roledefs['ycsb_public_ip']
    )


def ycsb_run_status(db):
    """ Shows just whether the jobs are complete"""
    database = get_db(db)
    with cd(database['home']):
        latest_out_log = run("ls -ltr | grep *.out | awk 'END{print}' | awk {'print $9'};")
        if len(latest_out_log) > 0:
            overall_marker = run('cat %s | grep "\[OVERALL\]" | wc -l' % latest_out_log)
            run('tail -n-4 %s' % latest_out_log)
            if int(overall_marker) > 0:
                #check for errors
                latest_err_log = run("ls -ltr | grep .err | awk 'END{print}' | awk {'print $9'};")
                lines_in_error_log = run('cat %s | wc -l' % latest_err_log)
                if int(lines_in_error_log) > 8:
                    ycsb.get_log(db)
                    raise Exception('Looks like there is something in the error log: %s : %s lines' % (latest_err_log, int(lines_in_error_log)) )
                print 'YCSB has completed on %s' % env.host
                return 1
    return 0

def job_complete(db):
    result = execute(
        ycsb_run_status,
        db,
        hosts=env.roledefs['ycsb_public_ip']
    )
    success = sum(result.values()) == len(env.roledefs['ycsb_public_ip'])
    return success

def await_completion(db):
    while not job_complete(db):
        print 'Polling (15) YCSB log files for completion status'
        time.sleep(15)

def log(line):
    print emphasis(line)
    with open(summary_log, "a") as myfile:
        myfile.write(line)

def growing_data_group_test(db, iter=10):
    os.remove(summary_log)
    kill_processes()
    delete_server_logs()
    with settings(warn_only=True):
        local('./archlogs.sh')

    log('This test will load approximately %sMB of data spread over %s runs' % (data['insertcount']*data['fieldcount']*data['fieldlength'] * iter, iter))

    while iter > 0:
        log('starting iteration '+iter)
        load(db)
        await_completion(db)
        run_status_check(db)
        download_logs(db)
        delete_server_logs()

        run_workload(db, 'A')
        await_completion(db)
        run_status_check(db)
        download_logs(db)
        delete_server_logs()

        run_workload(db, 'B')
        await_completion(db)
        run_status_check(db)
        download_logs(db)
        delete_server_logs()

        #move the key range up by the record count
        data['insertstart'] = data['insertstart'] + data['insertcount']
        data['recordcount'] = data['insertstart'] + data['insertcount']


        iter -= 1
        print log("Moving to round %s" % str(iter))









