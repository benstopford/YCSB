package com.yahoo.ycsb.db;

import com.yahoo.ycsb.Client;

import java.io.FileNotFoundException;

public class RunMongo {

    public static final int insertCount = 10000;
    public static final int operationCount = 10000;
    public static final int threadCount = 100;
    public static final int recordCount = 10000;
    public static final int fieldCount = 10;
    public static final int fieldLength = 20;
    public static final int cardinality = 1000;


    static String[] mongoLoad = new String[]{
            "-db",
            "com.yahoo.ycsb.db.MongoDbClient",
            "-s",
            "-p", "mongodb.url=54.154.71.170:27028,54.154.63.64:27028",
            "-p", "workload=com.yahoo.ycsb.workloads.CoreWorkload",
            "-p", "updateretrycount=1000",
            "-p", "mongodb.writeConcern=normal",
            "-p", "mongodb.database=ycsb",
            "-p", "recordcount="+recordCount,
            "-p", "fieldcount="+fieldCount,
            "-p", "threadcount="+threadCount,
            "-p", "insertretrycount=10",
            "-p", "fieldlengthdistribution=constant",
            "-p", "operationcount="+operationCount,
            "-p", "insertcount=" + insertCount,
            "-p", "mongodb.readPreference=primaryPreferred",
            "-p", "measurementtype=timeseries",
            "-p", "reconnectiontime=1000",
            "-p", "insertstart=0",
            "-p", "fieldlength="+fieldLength,
            "-p", "valuegenerator=queryable",
            "-p", "cardinality="+cardinality,
            "-load"};
    static String[] mongoRun = new String[]{
            "-db",
            "com.yahoo.ycsb.db.MongoDbClient",
            "-s",
            "-p", "mongodb.url=54.154.71.170:27028,54.154.63.64:27028",
            "-P", "workloads/workloadh",
            "-p", "updateretrycount=1000",
            "-p", "mongodb.writeConcern=normal",
            "-p", "mongodb.database=ycsb",
            "-p", "recordcount=" + recordCount,
            "-p", "fieldcount=" + fieldCount,
            "-p", "threadcount=" + threadCount,
            "-p", "insertretrycount=10",
            "-p", "fieldlengthdistribution=constant",
            "-p", "operationcount=" + operationCount,
            "-p", "insertcount=" + insertCount,
            "-p", "mongodb.readPreference=primaryPreferred",
            "-p", "measurementtype=timeseries",
            "-p", "reconnectiontime=1000",
            "-p", "insertstart=0",
            "-p", "fieldlength=" + fieldLength,
            "-p", "insertstart=0",

            "-p", "queryfield=field1",
            "-p", "valuegenerator=queryable",
            "-p", "cardinality=" + cardinality,

            "-t"};


    public static void main(String[] args) throws FileNotFoundException {
        if (args[0].equals("run"))
            new Client().main(mongoRun);
        else
            new Client().main(mongoLoad);


    }
}
