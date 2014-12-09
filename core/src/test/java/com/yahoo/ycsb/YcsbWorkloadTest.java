package com.yahoo.ycsb;

import com.yahoo.ycsb.db.TestDatabase;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.io.FileInputStream;
import java.io.IOException;
import java.util.List;
import java.util.Properties;

import static org.testng.Assert.assertEquals;
import static org.testng.Assert.assertTrue;

public class YcsbWorkloadTest {

    public static final String readOnlyWorkload = "src/test/conf/workloadc";

    @BeforeMethod
    public void setUp() {
        TestDatabase.clearState();
    }

    @Test
    public void shouldReadKeysMatchingOperationCount() throws IOException {
        Client.run(new String[]{
                        "-db", "com.yahoo.ycsb.db.TestDatabase",
                        "-t",
                        "-P", readOnlyWorkload,
                        "-p", "operationcount=65"
                }
                , new LoggingExitHandler()
        );

        assertEquals(TestDatabase.readCount, 65);
    }

    @Test
    public void shouldReadKeysMatchingOperationCountInFile() throws IOException {
        Client.run(new String[]{
                        "-db", "com.yahoo.ycsb.db.TestDatabase",
                        "-t",
                        "-P", readOnlyWorkload
                }
                , new LoggingExitHandler()
        );

        Properties workloada = new Properties();
        workloada.load(new FileInputStream(readOnlyWorkload));
        assertEquals(TestDatabase.readCount, integerOf(workloada.get("operationcount")));
    }


    @Test
    public void shouldDefineKeyspaceWithRecordCount() throws IOException {
        Client.run(new String[]{
                        "-db", "com.yahoo.ycsb.db.TestDatabase",
                        "-t",
                        "-P", readOnlyWorkload,
                        "-p", "operationcount=100",
                        "-p", "recordcount=50000",
                }
                , new LoggingExitHandler()
        );

        int max = maxCounter(TestDatabase.keysRequestedForRead);
        assertTrue(max <= 50000);
        assertTrue(max > 100);
        assertEquals(TestDatabase.readCount, 100);
    }

    private int maxCounter(List<String> keys) {
        int max = 0;
        for (String key : keys) {
            int numberPart = Integer.valueOf(key.substring(4, key.length()));
            if (numberPart > max) {
                max = numberPart;
            }
        }
        return max;
    }


    private int integerOf(Object property) {
        return Integer.valueOf((String) property).intValue();
    }
}
