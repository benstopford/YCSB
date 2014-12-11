import ycsb
from fabric.api import *
from helpers import get_db
import time
from util.print_utils import emphasis
from conf.workloads import conf
import helpers
import os
import time
import math
from amazonctl.db import db_up      as db_up
from amazonctl.db import db_down      as db_down
from fabfile.charts.table_parser import data_table, column_defs
from fabfile.charts.panda_parser import convert_to_panda


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
    print log('Load has been started: [%s / %s]' % (conf['insertstart'], conf['insertcount']))
    await_completion(db)
    run_status_check(db)
    download_logs(db)
    delete_server_logs()


def run_workload(db, wl):
    helpers.reset_base_time()
    execute(
        ycsb.run_workload,
        db,
        workload=wl,
        hosts=env.roledefs['ycsb_public_ip']
    )
    print log('Workload %s has been started' % wl)
    await_completion(db)
    run_status_check(db)
    download_logs(db)
    delete_server_logs()


def print_tail(db):
    database = get_db(db)
    with cd(database['home']):
        latest_log = run("ls -ltr | awk 'END{print}' | awk {'print $9'};")
        if len(latest_log) > 0:
            print run('tail -n-70 %s' % latest_log)


def run_status_check(db):
    print emphasis('STATUS CHECK START')
    execute(
        print_tail,
        db,
        hosts=env.roledefs['ycsb_public_ip']
    )
    print emphasis('STATUS CHECK END')


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
    """ Shows whether the job is:q complete"""
    database = get_db(db)
    with cd(database['home']):
        latest_out_log = run("ls -ltr | grep *.out | awk 'END{print}' | awk {'print $9'};")
        if len(latest_out_log) > 0:
            overall_marker = run('cat %s | grep "\[OVERALL\]" | wc -l' % latest_out_log)
            run('tail -n-4 %s' % latest_out_log)
            if int(overall_marker) > 0:
                # check for errors
                latest_err_log = run("ls -ltr | grep .err | awk 'END{print}' | awk {'print $9'};")

                permissible_errors = ''
                if 'permissablerunerrors' in get_db(db):
                    permissible_errors = " ".join(['| grep -v ' + s for s in get_db(db)['permissablerunerrors']])
                    print permissible_errors

                lines_in_error_log = run('cat %s %s | wc -l' % (latest_err_log, permissible_errors))
                if int(lines_in_error_log) > 8:
                    ycsb.get_log(db)
                    run('tail %s ' % latest_err_log)
                    raise Exception('Looks like there is something in the error log: %s : %s lines' % (
                        latest_err_log, int(lines_in_error_log)))
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
        myfile.write('%s\n' % line)


def archive_logs():
    with settings(warn_only=True):
        local('./archlogs.sh')


def initialise(kill_summary_log=True):
    log('starting run')

    if os.path.exists(summary_log) and kill_summary_log:
        os.remove(summary_log)

    kill_processes()
    delete_server_logs()
    archive_logs()


def load_action(db):
    # do the data load
    load(db)
    conf['insertstart'] = conf['insertstart'] + conf['insertcount']
    # rebuild the db
    db_down(db)
    db_up(db)


def run_until_throughput_stabalises(db, action):
    last_tp = 0
    one_before_that = 0
    for threads in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]:
        conf['threadcount'] = threads

        #Run the necessary action
        action(db)

        # Break out if throughput has stabalised
        raw = data_table('logs')
        df = convert_to_panda(raw, column_defs)
        throughput = df[df.threadcount == threads]['throughput'].mean()
        if last_tp > 0 and one_before_that > 0:
            # work out the deltas
            diff1 = throughput - last_tp
            diff2 = throughput - one_before_that
            #zero negative deltas as downward jumps can be considered noise
            if diff1 < 0:
                diff1 = 0
            if diff1 < 0:
                diff1 = 0
            #break if we have gone up by less than 10% in the last three runs?
            tenPercent = throughput * 0.1
            if diff1 < tenPercent and diff2 < tenPercent:
                log('we reached a maximum throughput at threadcount=%s : [%s]->[%s]->[%s]' % (
                    threads, one_before_that, last_tp, throughput))
                break

        log('Max throughput still not reached at threadcount=%s : [%s]->[%s]->[%s]' % (threads, one_before_that
                                                                                       , last_tp, throughput))
        one_before_that = last_tp
        last_tp = throughput


def find_optimum_threads_for_load(db):
    conf['insertstart'] = 0
    conf['insertcount'] = 6 * 1000
    conf['fieldcount'] = 1
    conf['fieldlength'] = 1000

    initialise()

    run_until_throughput_stabalises(db, load_action)


def workload_action(workload):
    return lambda db : run_workload(db, workload)


def find_optimum_threads_for_workload(db):
    initialise()

    # load test data: 100MB
    conf['insertstart'] = 0
    conf['insertcount'] = 100 * 1000
    conf['fieldcount'] = 1
    conf['fieldlength'] = 1000
    conf['threadcount'] = 30
    load(db)

    # should run for 90secs
    conf['operationcount'] = 100000000
    conf['recordcount'] = conf['insertcount']
    conf['maxexecutiontime'] = 90

    initialise(False)

    run_until_throughput_stabalises(db, workload_action('A'))


def growing_test(db, iterations=10, mode='run'):
    iter = int(iterations)

    log('This test will load approximately %sMB of data spread over %s runs' % (
        conf['insertcount'] * conf['fieldcount'] * conf['fieldlength'] * int(iter) / 1000000, iter))

    initialise()
    conf['insertstart'] = 0

    if mode != 'run':
        return

    while iter > 0:
        log('starting iteration %s.' % iter)
        start = time.time()

        # ensure there is no time limit for the load phase
        conf.pop('maxexecutiontime', None)

        load(db)

        # move the key range up by the record count
        conf['insertstart'] = conf['insertstart'] + conf['insertcount']
        conf['recordcount'] = conf['insertstart']

        # make the workload runs time limited
        conf['maxexecutiontime'] = 60 * 2

        run_workload(db, 'A')
        run_workload(db, 'B')
        run_workload(db, 'C')

        iter -= 1
        print log("Round %s took %smins" % (iter, (time.time() - start) / 60))

    log("all done")






