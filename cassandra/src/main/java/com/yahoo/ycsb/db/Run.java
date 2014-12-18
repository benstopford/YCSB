package com.yahoo.ycsb.db;

import com.yahoo.ycsb.Client;

import java.io.FileNotFoundException;
import java.util.Arrays;

public class Run {
    public static final int insertCount = 100;
    public static final int operationCount = 100;
    public static final int threadCount = 1;
    public static final int recordCount = 100;
    public static final int fieldCount = 30;
    public static final int fieldLength = 20;
    private static String queryField = "field0";
    public static final int cardinality = 3;
    public static final String hosts = "hosts=54.154.9.18";

    static String[] load = new String[]{
            "-db",
            "com.yahoo.ycsb.db.CassandraCQLClient",
            "-s",
            "-p", "workload=com.yahoo.ycsb.workloads.CoreWorkload",
            "-p", hosts,
            "-p", "updateretrycount=1000",
            "-p", "recordcount="+recordCount,
            "-p", "fieldcount="+fieldCount,
            "-p", "threadcount="+threadCount,
            "-p", "insertretrycount=10",
            "-p", "fieldlengthdistribution=constant",
            "-p", "operationcount="+operationCount,
            "-p", "insertcount=" + insertCount,
            "-p", "measurementtype=timeseries",
            "-p", "reconnectiontime=1000",
            "-p", "insertstart=0",
            "-p", "fieldlength="+fieldLength,
            "-p", "valuegenerator=queryable",
            "-p", "queryfield="+ queryField,
            "-p", "cardinality="+cardinality,
            "-load"};
    static String[] run = new String[]{
            "-db",
            "com.yahoo.ycsb.db.CassandraCQLClient",
            "-s",
            "-p", hosts,
            "-P", "workloads/workloadh",
            "-p", "updateretrycount=1000",
            "-p", "recordcount=" + recordCount,
            "-p", "fieldcount=" + fieldCount,
            "-p", "threadcount=" + threadCount,
            "-p", "insertretrycount=10",
            "-p", "fieldlengthdistribution=constant",
            "-p", "operationcount=" + operationCount,
            "-p", "insertcount=" + insertCount,
            "-p", "measurementtype=timeseries",
            "-p", "reconnectiontime=1000",
            "-p", "insertstart=0",
            "-p", "fieldlength=" + fieldLength,
            "-p", "queryfield="+ queryField,
            "-p", "valuegenerator=queryable",
            "-p", "cardinality=" + cardinality,
            "-t"};
    static String[] init = new String[]{
            "-db",
            "com.yahoo.ycsb.db.CassandraCQLClient",
            "-p", hosts,
            "-p", "queryfield="+ queryField,
            "-p", "fieldcount="+ fieldCount,
            "-init"
    };


    public static void main(String[] args) throws FileNotFoundException {


        System.out.println(Arrays.asList(args));

//        new Client().run(init, exit());
        new Client().run(run, exit());
    }

    private static Client.ExitHandler exit() {
        return new Client.ExitHandler() {
            @Override
            public void exit() {
                System.out.println("exiting");
                System.exit(0);
            }
        };
    }
}
