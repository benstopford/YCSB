package com.yahoo.ycsb;

import org.testng.annotations.Test;

import java.util.HashSet;

import static org.testng.Assert.assertEquals;
import static org.testng.Assert.assertTrue;
import static org.testng.Assert.fail;

public class CardinalityBasedFieldCreatorTest {


    @Test
    public void shouldCreateFieldsBasedOnCardinality() {
        int cardinality = 12;
        int length = 10;

        CardinalityBasedFieldCreator thing = new CardinalityBasedFieldCreator(cardinality, length);
        HashSet fields = new HashSet();
        for (int i = 0; i < 1000; i++) {
            fields.add(thing.nextValue().toString());

        }
        assertEquals(fields.size(), cardinality);
    }

    @Test
    public void paddingShouldBeAscii() {
        int cardinality = 12;
        int length = 10;

        CardinalityBasedFieldCreator thing = new CardinalityBasedFieldCreator(cardinality, length);
        char[] value = thing.nextValue().toString().toCharArray();
        for (char c : value) {
            assertTrue((int) c >= 48, "Not a character or number: '" + String.valueOf(c) + "' char with number " + (int) c);
            assertTrue((int) c <= 122, "Not a character or number: '" + String.valueOf(c) + "' char with number " + (int) c);
        }
    }

    @Test
    public void shouldFailIfCardinalityTooLargeToRepresentInValueLength() {
        int cardinality = Integer.MAX_VALUE;
        int length = 1;
        try {
            new CardinalityBasedFieldCreator(cardinality, length);
            fail("Exception should have been thrown");
        } catch (Exception e) {

        }
    }


}
