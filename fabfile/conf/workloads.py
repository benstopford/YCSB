root = '/opt/ycsb'  # root of YCSB installation
# TIME_DURATION = 20*60  #seconds

data = {
    # global YSCB properties
    'operationcount': 1000000,    #Total operations (writes or reads during a workload)
    'insertcount':    1000000,    #How many objects to write during load phase
    'recordcount':    1000000,    #Specifies the keyspaace for reads

    'fieldcount': 1,          # the value is a list of this many byte arrays
    'fieldlength': 1000,       # either exactly or approximately this length depending on fieldlengthdistribution
    'fieldlengthdistribution': 'constant',  # can also be zipfian or uniform but zipfian isn't working currently

    'threadcount': 20,
    'workload': 'com.yahoo.ycsb.workloads.CoreWorkload',
    'exportmeasurementsinterval': 30000,


    'insertretrycount': 10,
    'ignoreinserterrors': 'true',
    'readretrycount': 1000,
    'updateretrycount': 1000,
    'measurementtype': 'timeseries',
    'timeseries.granularity': 100,  # Interval for reporting in ms

    'reconnectiontime': 1000


    #'fieldnameprefix': 'f',
    # 'maxexecutiontime': TIME_DURATION,      # 40min
    #'warmupexecutiontime': 60000,
    #'reconnectiontime': 5000, # 5 sec limit before reconnection
    # 'reconnectionthroughput': 10, #limit for reconnection.
    #'retrydelay': 1,
    #'readallfields': 'false',
    #'writeallfields': 'false',
    #'maxexecutiontime': 600,
    #'mongodb.writeConcern': 'replicas_safe',#Mongo SYNC only!

}

workloads = {
    'A': {  # Heavy Update workload
            'name': 'workloada',  #name of the workload to be part of the log files
            'propertyfiles': [root + '/workloads/workloada'],  #workload properties files
    },
    'B': {  # Mostly Read workload
            'name': 'workloadb',
            'propertyfiles': [root + '/workloads/workloadb'],
    },
    'C': {  # Read Only workload
            'name': 'workloadc',
            'propertyfiles': [root + '/workloads/workloadc'],
            'properties': {  #additional workload properties, overrides the global ones
                #'maxexecutiontime': 60000,
            },
    },
    'G': {  # Mostly Update workload
            'name': 'workloadg',
            'propertyfiles': [root + '/workloads/workloadg'],
    },
}
