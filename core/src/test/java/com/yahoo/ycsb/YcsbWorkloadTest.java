package com.yahoo.ycsb;

import com.yahoo.ycsb.db.TestDatabase;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.io.FileInputStream;
import java.io.IOException;
import java.util.List;
import java.util.Properties;

import static java.lang.Thread.sleep;
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
    public void shouldDefineKeyspaceRecordCount() throws IOException {
        Client.run(new String[]{
                        "-db", "com.yahoo.ycsb.db.TestDatabase",
                        "-t",
                        "-P", readOnlyWorkload,
                        "-p", "operationcount=100",
                        "-p", "recordcount=15",
                }
                , new LoggingExitHandler()
        );

        int max = maxKeyIdentifier(TestDatabase.keysRequestedForRead);
        assertTrue(max <= 15);
    }

    @Test
    public void zipifanShouldFavourCentre() throws IOException, InterruptedException {
        //Just prints out the different distributions
        for(String dist : new String[]{"uniform", "zipfian", "hotspot",  "latest"}) {
            Client.run(new String[]{
                            "-db", "com.yahoo.ycsb.db.TestDatabase",
                            "-t",
                            "-P", readOnlyWorkload,
                            "-p", "operationcount=100",
                            "-p", "recordcount=1000",
                            "-p", "requestdistribution="+dist
                    }
                    , new LoggingExitHandler()
            );
            System.out.println(dist+":");
            print(bucket(TestDatabase.keysRequestedForRead, 10));
        }
        sleep(2000);
    }

    private void print(int[] buckets) {
        int count = 0;
        for(int i: buckets){
            System.out.printf("Bucket %s has item count: %s\n", count++, i);
        }
    }

    private int[] bucket(List<String> keys, int numberOfBuckets) {
        int[] buckets = new int[numberOfBuckets];
        for (String key : keys) {
            int numberPart = Integer.valueOf(key.substring(4, key.length()));
            int bucket = numberPart % numberOfBuckets;
            buckets[bucket]++;
        }
        return buckets;
    }

    private int maxKeyIdentifier(List<String> keys) {
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
