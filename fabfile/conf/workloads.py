root = '/opt/ycsb'  #root of YCSB installation
TIME_DURATION = 20*60  #seconds

data = {
    #global YSCB properties
    'insertstart':0,                        #Increase this if there is already data in the DB
    'recordcount':  10000,                #not sure this is what it says it is. insert count appears to cover inserted data
    'operationcount': 10000,              #Total operations (writes or reads)
    'insertcount': 10000,                 #how many to write during load

    'fieldcount': 10,                      # the value is a list of this many byte arrays
    'fieldlength': 10,                     # each of the byte arrays is either exactly or approximately this length depending on the policy
    'fieldlengthdistribution':'zipfian',   # can also be constant or uniform

    #'fieldnameprefix': 'f',
    'maxexecutiontime': TIME_DURATION,      # 40min
    'threadcount': 30,
    'workload': 'com.yahoo.ycsb.workloads.CoreWorkload',
    'exportmeasurementsinterval': 30000,
    #'warmupexecutiontime': 60000,

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
TIME_DURATION = 20*60 #seconds


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
