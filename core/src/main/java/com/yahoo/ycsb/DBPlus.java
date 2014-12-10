package com.yahoo.ycsb;

public abstract class DBPlus extends DB {

    /**
     * Used in distributed instances of YCSB to initialise the cluster. This call should only be made once cluster-wide.
     * The implementation should prepare the database for YCSB use (create necessary tables etc)
     * @return
     */
    public abstract int initialiseTablesEtc() throws DBException;

}
