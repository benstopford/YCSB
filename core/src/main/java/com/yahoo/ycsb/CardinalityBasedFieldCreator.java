package com.yahoo.ycsb;

import java.util.Arrays;
import java.util.Random;

public class CardinalityBasedFieldCreator {
    private int cardinality;
    private int length;
    private Random random = new Random();

    public CardinalityBasedFieldCreator(int cardinality, int length) {
        this.cardinality = cardinality;
        this.length = length;
        checkLength(getPrefixBytes());
    }

    public ByteIterator nextValue() {
        byte[] prefixBytes = getPrefixBytes();
        return new ByteArrayByteIterator(padToLength(prefixBytes, length));
    }

    private byte[] getPrefixBytes() {
        int prefix = Math.abs(random.nextInt()) % cardinality;
        return String.valueOf(prefix).getBytes();
    }

    private byte[] padToLength(byte[] stringPrefix, int length) {
        byte[] byteValue = new byte[length];
        Arrays.fill(byteValue, (byte)66);
        for(int i = 0; i < stringPrefix.length; i++){
            byteValue[i] = stringPrefix[i];
        }
        return byteValue;
    }

    private void checkLength(byte[] stringPrefix) {
        if (stringPrefix.length > length) {
            throw new RuntimeException(String.format("Configured field length of %s is too short to support a cardinality of %s", length, cardinality));
        }
    }

}
