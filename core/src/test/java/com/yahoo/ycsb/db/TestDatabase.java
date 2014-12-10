package com.yahoo.ycsb.db;

import com.yahoo.ycsb.ByteIterator;
import com.yahoo.ycsb.DB;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TestDatabase extends DB {
    public static int insertCount = 0;
    public static int readCount = 0;
    public static List<String> keysRequestedForRead = new ArrayList<String>();
    public static HashMap<String, Map<String, ByteIterator>> insertData = new HashMap<String, Map<String, ByteIterator>>();

    public static void clearState() {
        insertCount = 0;
        readCount = 0;
        insertData = new HashMap();
        keysRequestedForRead = new ArrayList<String>();
    }

    @Override
    public int readOne(String table, String key, String field, Map<String, ByteIterator> result) {
        keysRequestedForRead.add(key);
        readCount++;
        return 0;
    }

    @Override
    public int readAll(String table, String key, Map<String, ByteIterator> result) {
        keysRequestedForRead.add(key);
        readCount++;
        return 0;
    }

    @Override
    public int scanAll(String table, String startkey, int recordcount, List<Map<String, ByteIterator>> result) {
        return 0;
    }

    @Override
    public int scanOne(String table, String startkey, int recordcount, String field, List<Map<String, ByteIterator>> result) {
        return 0;
    }

    @Override
    public int updateOne(String table, String key, String field, ByteIterator value) {
        return 0;
    }

    @Override
    public int updateAll(String table, String key, Map<String, ByteIterator> values) {
        return 0;
    }

    @Override
    public int insert(String table, String key, Map<String, ByteIterator> values) {
        insertCount++;
        insertData.put(key, values);
        return 0;
    }

    @Override
    public int delete(String table, String key) {
        return 0;
    }
}