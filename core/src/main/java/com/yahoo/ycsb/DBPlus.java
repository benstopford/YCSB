package com.yahoo.ycsb;

import java.util.HashMap;
import java.util.Map;

public abstract class DBPlus extends DB {

    /**
     * Used in distributed instances of YCSB to initialise the cluster. This call should only be made once cluster-wide.
     * The implementation should prepare the database for YCSB use (create necessary tables etc)
     * @return
     */
    public abstract int initialiseTablesEtc() throws DBException;

    public abstract int insertBatch(String table, Map<String, HashMap<String,ByteIterator>> batch);
}
