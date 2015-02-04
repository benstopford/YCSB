from amazonctl.db import db_up
from amazonctl.db import db_down
from amazonctl.ec2 import ec2_up
from charts.table_parser import data_table, column_defs
from charts.panda_parser import convert_to_panda
from charts.chart import insert_data_into_chart, throughput
from experiment_util import *



def _initialise():
    clear_log()
    log('initialising')
    kill_processes()
    delete_server_logs()
    archive_logs()


def _load_action(db):
    load(db)
    conf['insertstart'] = conf['insertstart'] + conf['insertcount']
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


def _set_test_duration(execution_time):
    # Override relevant setting to ensure we run for the specified execution_time
    conf['operationcount'] = 100000000
    conf['recordcount'] = conf['insertcount']
    conf['maxexecutiontime'] = execution_time
    conf['cardinality'] = (conf['insertcount'] / 10)


def _find_optimum_threads_for_workload(db, thread_start, workload, execution_time=60):
    _set_test_duration(execution_time)
    return _run_until_throughput_stabalises(db, workload_action(workload), thread_start)


def find_max_load_throughput(db):
    """Measures maximum throughput for the data loading phase"""
    conf['insertstart'] = 0
    conf['insertcount'] = 6 * 1000
    conf['fieldcount'] = 1
    conf['fieldlength'] = 1000
    _initialise()
    _run_until_throughput_stabalises(db, _load_action)

def find_max_workload_throughput(db, workload='A', thread_start=1):
    """Measures maximum throughput (i.e. optimal number of threads) for a single, specified workload"""
    _initialise()
    return _find_optimum_threads_for_workload(db, thread_start, workload)


def sequential_workloads(db, thread_start=1, execution_time=60, mb=1000, include_load=True):
    """Measures max throughput for a collection of different workloads"""
    thread_start = int(thread_start)
    execution_time = int(execution_time)
    mb = int(mb)
    include_load = bool(include_load)

    _initialise()
    log("Starting simple max load test for a %s nodes and datasize of %sMB" % (running_db_node_count(), mb))

    results = []

    if include_load:
        _load(db, mb)

    for workload in ['A', 'B', 'C', 'H']:
        result = _find_optimum_threads_for_workload(db, thread_start, workload, execution_time)
        results.append([workload, result[0], result[1]])

    log("Final result was: %s" % results)


def node_growth(db, start=2, end=8, thread_start=20, workload='H', execution_time=60, mb=100):
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

    _initialise()
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


def data_growth(db, iterations=10, mode='run'):
    """Increases the amount of data in the database iteratively, measuring and charting the max
     throughput for each iteration."""
    iter = int(iterations)

    log('This test will load approximately %sMB of data spread over %s runs' % (
        conf['insertcount'] * conf['fieldcount'] * conf['fieldlength'] * int(iter) / 1000000, iter))

    _initialise()
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






