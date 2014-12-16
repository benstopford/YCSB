package com.yahoo.ycsb;

import java.util.concurrent.atomic.AtomicLong;

public class MeasurementTracker {

    protected static AtomicLong consumedBytes = new AtomicLong();
    protected static AtomicLong queryResultCount = new AtomicLong();

    public static void reset() {
        consumedBytes = new AtomicLong();
        queryResultCount = new AtomicLong();

    }

    public static void incrementConsumedBytes(long by) {
        while (true) {
            long current = consumedBytes.get();
            long next = current + by;

            if (consumedBytes.compareAndSet(current, next)) {
                return;
            }
        }
    }

    public static void incrementQueryResultCount(long by) {
        while (true) {
            long current = queryResultCount.get();
            long next = current + by;

            if (queryResultCount.compareAndSet(current, next)) {
                return;
            }
        }
    }

    public static long getConsumedBytes() {
        return consumedBytes.longValue();
    }

    public static long getQueryResultCount() {
        return queryResultCount.longValue();
    }
}
