import ycsb
import time
import os
import helpers
from fabric.api import *
from helpers import get_db
from util.print_utils import emphasis, log, clear_log
from amazonctl.db import db_up
from amazonctl.db import db_down
from amazonctl.ec2 import ec2_up
from charts.table_parser import data_table, column_defs
from charts.panda_parser import convert_to_panda
from charts.chart import insert_data_into_chart, throughput
from conf.workloads import conf
from conf.hosts import running_db_node_count, running_ycsb_node_count, host_counts, addresses


def delete_server_logs():
    if running_ycsb_node_count() > 0:
        execute(
            ycsb.do_clean,
            hosts=addresses()['ycsb_public_ip']
        )


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
    execute(
        ycsb.do_get_log,
        db,
        hosts=addresses()['ycsb_public_ip']
    )


def kill_processes():
    if running_ycsb_node_count() > 0:
        execute(
            ycsb.do_kill,
            hosts=addresses()['ycsb_public_ip']
        )


def ycsb_run_status(db):
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

            lines_in_error_log = run('cat %s %s | wc -l' % (latest_err_log, permissible_errors))
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
        ycsb_run_status,
        db,
        hosts=first_host
    )

    # if done check the others
    if success > 0:
        result = execute(
            ycsb_run_status,
            db,
            hosts=addresses()['ycsb_public_ip']
        )
        success = sum(result.values()) == running_ycsb_node_count()
        return success

    return 0


def await_completion(db):
    while not job_complete(db):
        print 'Polling (15) YCSB log files for completion status'
        time.sleep(15)


def archive_logs():
    with settings(warn_only=True):
        local('./archlogs.sh')


def initialise():
    clear_log()
    log('initialising')

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


def _run_until_throughput_stabalises(db, action, thread_start=1):
    thread_count = -1
    throughput = 0
    last_tp = 0
    one_before_that = 0
    for threads in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]:
        if threads < thread_start:
            continue

        conf['threadcount'] = threads

        # Run the necessary action
        action(db)

        # Break out if throughput has stabalised
        raw = data_table('logs')
        df = convert_to_panda(raw, column_defs)
        throughput = df[df.threadcount == threads]['throughput'].mean()
        if last_tp > 0 and one_before_that > 0:
            # work out the deltas
            diff1 = throughput - last_tp
            diff2 = throughput - one_before_that
            # zero negative deltas as downward jumps can be considered noise
            if diff1 < 0:
                diff1 = 0
            if diff1 < 0:
                diff1 = 0
            # break if we have gone up by less than 10% in the last three runs?
            tenPercent = throughput * 0.1
            if diff1 < tenPercent and diff2 < tenPercent:
                log('we reached a maximum throughput at threadcount=%s : [%s]->[%s]->[%s]' % (
                    threads, one_before_that, last_tp, throughput))
                thread_count = threads
                break

        log('Max throughput still not reached at threadcount=%s : [%s]->[%s]->[%s]' % (threads, one_before_that
                                                                                       , last_tp, throughput))
        one_before_that = last_tp
        last_tp = throughput

    return thread_count, throughput


def find_optimum_threads_for_load(db):
    conf['insertstart'] = 0
    conf['insertcount'] = 6 * 1000
    conf['fieldcount'] = 1
    conf['fieldlength'] = 1000

    initialise()

    _run_until_throughput_stabalises(db, load_action)


def workload_action(workload):
    return lambda db: run_workload(db, workload)


def _load(db, mb=1000):
    conf['insertstart'] = 0
    conf['insertcount'] = mb * 1000
    conf['fieldcount'] = 10
    conf['fieldlength'] = 100
    conf['threadcount'] = 30
    conf['cardinality'] = (conf['insertcount'] / 10)
    load(db)
    log("Load completed %sMB" % mb)

def _find_optimum_threads_for_workload(db, thread_start, workload, execution_time=60):
    # should run for 90secs
    conf['operationcount'] = 100000000
    conf['recordcount'] = conf['insertcount']
    conf['maxexecutiontime'] = execution_time
    conf['cardinality'] = (conf['insertcount'] / 10)
    return _run_until_throughput_stabalises(db, workload_action(workload), thread_start)


def find_optimum_threads_for_workload(db, workload='A', thread_start=1):
    initialise(kill_summary_log)

    return _find_optimum_threads_for_workload(db, thread_start, workload)


def simple_max_load_test_multi_workload(db, thread_start=1, execution_time=60, mb=1000, include_load=True):
    """Loads specified data into a database """
    thread_start = int(thread_start)
    execution_time = int(execution_time)
    mb = int(mb)
    include_load = bool(include_load)

    initialise()
    log("Starting simple max load test for a %s nodes and datasize of %sMB" % (running_db_node_count(), mb))

    results = []

    if include_load:
        _load(db, mb)

    for workload in ['A', 'B', 'C', 'H']:
        result = _find_optimum_threads_for_workload(db, thread_start, workload, execution_time)
        results.append([workload, result[0], result[1]])

    log("Final result was: %s" % results)


def node_growth_test(db, start=2, end=8, thread_start=20, workload='H', execution_time=60, mb=100):
    """ Establishes the maximum throughput, for a given workload, running
        on an increasingly larger cluster of machines.
        The test increments the number of machines by one,
        starting from the current number of running machines. For each
        configuration: load data, run specified workload using
        an increasing number of threads until throughput stabalises, then
        increase the number of machines in the cluster and repeat.
    Parameters:
        start = the number of servers to start with if more are not already running
        end = the max number of servers to scale to
        thread_start = number of threads to start with, defaults to 1
        workload = the ycsb workload to run
        execution_time = how long to run the workload for to establish throughput
    """
    start = int(start)
    end = int(end)
    thread_start = int(thread_start)
    execution_time = int(execution_time)
    mb = int(mb)

    initialise()
    log("Starting node growth test from: %s => %s" % (running_db_node_count(), end))

    # Start DB nodes if needed
    if start > running_db_node_count():
        host_counts['DB'] = start

    # We need at least as many ycsb nodes as db nodes at the end of the test
    if end > running_ycsb_node_count():
        host_counts['YCSB'] = end

    # Boot everything
    ec2_up(db)
    ycsb.deploy()

    db_up(db)

    results = []
    for node_count in range(running_db_node_count(), end + 1):

        # increase machine count only if needed
        if (node_count > running_db_node_count()):
            host_counts['DB'] = node_count
            ec2_up(db)
            db_up(db)
            log('%s Cluster has been upgraded to %s nodes' % (db, running_db_node_count()))
        if mb > 0:
            _load(db, mb)

        # Run the workload
        result = _find_optimum_threads_for_workload(db, thread_start, workload, execution_time)

        # Use the previous threadcount but one as our starting point for the next run (makes the
        # assumption that increasing the number of servers increases the throughput of the database
        thread_start = result[0] / 2

        results.append([node_count, result[0], result[1]])

    log("Final result was: %s" % results)


def data_growth_test(db, iterations=10, mode='run'):
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

        insert_data_into_chart(throughput('../logs'))

    log("all done")






