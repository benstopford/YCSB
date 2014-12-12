package com.yahoo.ycsb.db;

import com.yahoo.ycsb.ByteIterator;
import com.yahoo.ycsb.DBException;
import com.yahoo.ycsb.DBPlus;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TestDatabase extends DBPlus {
    public static int insertCount = 0;
    public static int readCount = 0;
    public static List<String> keysRequestedForRead = new ArrayList<String>();
    public static HashMap<String, Map<String, ByteIterator>> insertData = new HashMap<String, Map<String, ByteIterator>>();
    public static List<String[]> querys = new ArrayList<String[]>();

    public static void clearState() {
        insertCount = 0;
        readCount = 0;
        insertData = new HashMap();
        keysRequestedForRead = new ArrayList<String>();
        querys = new ArrayList<String[]>();
    }

    @Override
    public int readOne(String table, String key, String field, Map<String, ByteIterator> result) {
        System.out.println("TestDatabase.readOne called");
        keysRequestedForRead.add(key);
        readCount++;
        return 0;
    }

    @Override
    public int readAll(String table, String key, Map<String, ByteIterator> result) {
        System.out.println("TestDatabase.readAll called");
        keysRequestedForRead.add(key);
        readCount++;
        return 0;
    }

    @Override
    public int scanAll(String table, String startkey, int recordcount, List<Map<String, ByteIterator>> result) {
        System.out.println("TestDatabase.scanOne called");
        return 0;
    }

    @Override
    public int scanOne(String table, String startkey, int recordcount, String field, List<Map<String, ByteIterator>> result) {
        System.out.println("TestDatabase.scanOne called");
        return 0;
    }

    @Override
    public int updateOne(String table, String key, String field, ByteIterator value) {

        System.out.println("TestDatabase.updateOne called");
        return 0;
    }

    @Override
    public int updateAll(String table, String key, Map<String, ByteIterator> values) {
        System.out.println("TestDatabase.udpateAll called");
        return 0;
    }

    @Override
    public int insert(String table, String key, Map<String, ByteIterator> values) {
        System.out.println("TestDatabase.insert called");
        insertCount++;
        insertData.put(key, values);
        return 0;
    }

    @Override
    public int delete(String table, String key) {
        System.out.println("TestDatabase.delete called");
        return 0;
    }

    @Override
    public int initialiseTablesEtc() throws DBException {

        System.out.println("TestDatabase.initialiseTables called");
        return 0;
    }

    @Override
    public int insertBatch(String table, Map<String, HashMap<String, ByteIterator>> batch) {

        System.out.println("TestDatabase.insertBatch called");
        return 0;
    }

    @Override
    public int query(String table, String field, String searchTerm) {
        System.out.println("TestDatabase.query called");
        querys.add(new String[]{
                field, searchTerm
        });
        return 0;
    }
}