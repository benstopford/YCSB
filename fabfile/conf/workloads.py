root = '/opt/ycsb'  # root of YCSB installation
# TIME_DURATION = 20*60  #seconds


conf = {
    ## Key YSCB properties: ##
    'operationcount': 1000,                 # Total operations (writes or reads during a workload)
    'insertcount': 1000,                    # How many objects to write during load phase
    'recordcount': 1000,                    # Specifies the keyspaace for reads
        'fieldcount': 30,                   #the value is a list of this many byte arrays
    'fieldlength': 100,                     #either exactly or approximately this length depending on fieldlengthdistribution
    'fieldlengthdistribution': 'constant',  # can also be zipfian or uniform but zipfian isn't working currently
    # 'maxexecutiontime': 90,               #Stops the run after a set amount of time


    #Only used for the query extension:
    # 'valuegenerator': 'queryable',
    # 'queryfield': 'field0',
    # 'cardinality': 1000 / 10, #set as a fraction of the insertcount

    'threadcount': 5,
    'workload': 'com.yahoo.ycsb.workloads.CoreWorkload',
    'exportmeasurementsinterval': 30000,
    'insertretrycount': 10,
    'ignoreinserterrors': 'true',
    'readretrycount': 1000,
    'updateretrycount': 1000,
    'measurementtype': 'timeseries',
    'timeseries.granularity': 100,
    'reconnectiontime': 1000,
}

workloads = {
    'A': {  # Heavy Update workload
            'name': 'workloada',  # name of the workload to be part of the log files
            'propertyfiles': [root + '/workloads/workloada'],  #workload properties files
    },
    'B': {  # Mostly Read workload
            'name': 'workloadb',
            'propertyfiles': [root + '/workloads/workloadb'],
    },
    'C': {  # Read Only workload
            'name': 'workloadc',
            'propertyfiles': [root + '/workloads/workloadc'],
            'properties': {  # additional workload properties, overrides the global ones
                #'maxexecutiontime': 60000,
            },
    },
    'G': {  # Mostly Update workload
            'name': 'workloadg',
            'propertyfiles': [root + '/workloads/workloadg'],
    },    'H': {  # Query workload
            'name': 'workloadh',
            'propertyfiles': [root + '/workloads/workloadh'],
    },
}
