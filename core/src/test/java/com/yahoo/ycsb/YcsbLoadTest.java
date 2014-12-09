package com.yahoo.ycsb;

import com.yahoo.ycsb.db.TestDatabase;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Map;
import java.util.Properties;

import static org.testng.Assert.assertEquals;

public class YcsbLoadTest {

    public static final String workloadFile = "src/test/conf/workloada";

    @BeforeMethod
    public void setUp() {
        TestDatabase.clearState();
    }

    @Test
    public void shouldDefaultInsertsToRecordCountFromWorkloadFile() throws IOException {
        Client.run(new String[]{
                        "-db", "com.yahoo.ycsb.db.TestDatabase",
                        "-load",
                        "-P", workloadFile
                }
                , new LoggingExitHandler()
        );

        Properties workloada = new Properties();
        workloada.load(new FileInputStream(workloadFile));
        assertEquals(TestDatabase.insertCount, integerOf(workloada.get("recordcount")));
    }

    private int integerOf(Object property) {
        return Integer.valueOf((String) property).intValue();
    }

    @Test
    public void shouldDefaultInsertsToRecordCountOverride() throws IOException {
        Client.run(new String[]{
                        "-db", "com.yahoo.ycsb.db.TestDatabase",
                        "-load",
                        "-P", workloadFile,
                        "-p", "recordcount=66"
                }
                , new LoggingExitHandler()
        );

        assertEquals(TestDatabase.insertCount, 66);
    }


    @Test
    public void shouldDefineInsertsByInsertCountPropertyOverRecordCountProperty() throws IOException {
        Client.run(new String[]{
                        "-db", "com.yahoo.ycsb.db.TestDatabase",
                        "-load",
                        "-P", workloadFile,
                        "-p", "recordcount=66",
                        "-p", "insertcount=77"
                }
                , new LoggingExitHandler()
        );

        assertEquals(TestDatabase.insertCount, 77);
    }


    @Test
    public void shouldWriteExpectedNumberOfBytes() throws FileNotFoundException {
        Client.run(new String[]{
                        "-db", "com.yahoo.ycsb.db.TestDatabase",
                        "-load",
                        "-P", workloadFile,
                        "-p", "insertcount=100",
                        "-p", "fieldlength=10",
                        "-p", "fieldcount=10"
                }
                , new LoggingExitHandler()
        );

        //YCSB values are a map of string keys to byte arrays
        long actualData = 0;
        for(String key: TestDatabase.insertData.keySet()){
            actualData+=key.getBytes().length;
            Map<String, ByteIterator> value = TestDatabase.insertData.get(key);
            for(String field: value.keySet()){
                ByteIterator fieldContents = value.get(field);
                actualData+=field.getBytes().length;
                actualData+=fieldContents.toArray().length;
            }
        }

        assertEquals(actualData, 16590);
        //NB we might have expected 10K but each field has a string key in addition to the byte array
    }

    @Test
    public void shouldWriteUniqueKeys() throws FileNotFoundException {
        Client.run(new String[]{
                        "-db", "com.yahoo.ycsb.db.TestDatabase",
                        "-load",
                        "-P", workloadFile,
                        "-p", "insertcount=100",
                }
                , new LoggingExitHandler()
        );
        assertEquals(TestDatabase.insertData.keySet().size(), 100);
    }


}
