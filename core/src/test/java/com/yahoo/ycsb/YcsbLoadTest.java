package com.yahoo.ycsb;

import com.yahoo.ycsb.db.TestDatabase;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.HashSet;
import java.util.Map;
import java.util.Properties;

import static org.testng.Assert.assertEquals;

public class YcsbLoadTest extends TestBase {


    @BeforeMethod
    public void setUp() {
        TestDatabase.clearState();
    }

    @Test
    public void shouldDefaultInsertsToRecordCountFromreadOnlyWorkload() throws IOException {
        Client.run(new String[]{
                        "-db", "com.yahoo.ycsb.db.TestDatabase",
                        "-load",
                        "-P", readOnlyWorkload
                }
                , new LoggingExitHandler()
        );

        Properties workloada = new Properties();
        workloada.load(new FileInputStream(readOnlyWorkload));
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
                        "-P", emptyWorkload,
                        "-p", "recordcount=6"
                }
                , new LoggingExitHandler()
        );

        assertEquals(TestDatabase.insertCount, 6);
    }


    @Test
    public void shouldDefineInsertsByInsertCountPropertyOverRecordCountProperty() throws IOException {
        Client.run(new String[]{
                        "-db", "com.yahoo.ycsb.db.TestDatabase",
                        "-load",
                        "-P", emptyWorkload,
                        "-p", "recordcount=6",
                        "-p", "insertcount=8"
                }
                , new LoggingExitHandler()
        );

        assertEquals(TestDatabase.insertCount, 8);
    }


    @Test
    public void shouldWriteExpectedNumberOfBytes() throws FileNotFoundException {
        Client.run(new String[]{
                        "-db", "com.yahoo.ycsb.db.TestDatabase",
                        "-load",
                        "-P", emptyWorkload,
                        "-p", "insertcount=100",
                        "-p", "recordcount=100",
                        "-p", "fieldlength=10",
                        "-p", "fieldcount=10"
                }
                , new LoggingExitHandler()
        );

        //YCSB values are a map of string keys to byte arrays
        long actualData = 0;
        for (String key : TestDatabase.insertData.keySet()) {
            actualData += key.getBytes().length;
            Map<String, ByteIterator> value = TestDatabase.insertData.get(key);
            for (String field : value.keySet()) {
                ByteIterator fieldContents = value.get(field);
                actualData += field.getBytes().length;
                actualData += fieldContents.toArray().length;
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
                        "-P", emptyWorkload,
                        "-p", "insertcount=10",
                        "-p", "recordcount=10",
                }
                , new LoggingExitHandler()
        );
        assertEquals(TestDatabase.insertData.keySet().size(), 10);
    }

    @Test
    public void shouldWriteQueryableData() throws FileNotFoundException, InterruptedException {
        Client.run(new String[]{
                        "-db", "com.yahoo.ycsb.db.TestDatabase",
                        "-load",
                        "-P", emptyWorkload,
                        "-p", "valuegenerator=queryable",
                        "-p", "queryfield=field1",
                        "-p", "cardinality=5",
                        "-p", "insertcount=100",
                        "-p", "recordcount=100",
                }
                , new LoggingExitHandler()
        );
        assertEquals(TestDatabase.insertData.keySet().size(), 100);

        HashSet uniqueValues = new HashSet();
        for (Map<String,ByteIterator> row : TestDatabase.insertData.values()){
            String cell = row.get("field1").toString();
            uniqueValues.add(cell);
        }
        assertEquals(uniqueValues.size(), 5, "Should have had 5 entries but had: "+uniqueValues.size());
    }


}
