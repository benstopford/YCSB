root = '/opt/ycsb'  #root of YCSB installation

TIME_DURATION = 20*60 #seconds

data = {
    #global YSCB properties
    'insertstart':1000500,
    'recordcount':  1000000,    #RAM
    'fieldcount': 10,
    'fieldlength': 10,
    #'fieldnameprefix': 'f',
    'operationcount': 1000000,
    'maxexecutiontime': TIME_DURATION,      # 40min
    'threadcount': 30,
    'workload': 'com.yahoo.ycsb.workloads.CoreWorkload',
    'exportmeasurementsinterval': 30000,
    #'warmupexecutiontime': 60000,
    
    #'insertretrycount': 1000000000, #for Couchbase2 200M load
    'insertretrycount': 10,

    'ignoreinserterrors': 'false',
    'readretrycount': 1000,
    'updateretrycount': 1000,
    'measurementtype': 'timeseries',
    'timeseries.granularity': 100, # Interval for reporting in ms
    #'reconnectiontime': 5000, # 5 sec limit before reconnection
    'reconnectionthroughput': 10, #limit for reconnection.
    #'retrydelay': 1,
    #'readallfields': 'false',
    #'writeallfields': 'false',
    #'maxexecutiontime': 600,
    #'mongodb.writeConcern': 'replicas_safe',#Mongo SYNC only!
    'reconnectiontime': 1000,
}

workloads = {
    'A': {  #Heavy Update workload
        'name': 'workloada',    #name of the workload to be part of the log files
        'propertyfiles': [ root + '/workloads/workloada' ], #workload properties files
    },
    'B': {  #Mostly Read workload
        'name': 'workloadb',
        'propertyfiles': [ root + '/workloads/workloadb' ],
    },
    'C': {  #Read Only workload
        'name': 'workloadc',
        'propertyfiles': [ root + '/workloads/workloadc' ],
        'properties': {     #additional workload properties, overrides the global ones
            #'maxexecutiontime': 60000,
        },
    },
    'G': {  #Mostly Update workload
        'name': 'workloadg',
        'propertyfiles': [ root + '/workloads/workloadg' ],
    },
}
