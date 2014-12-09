package com.yahoo.ycsb.db;

import com.yahoo.ycsb.Client;

import java.io.FileNotFoundException;
import java.util.Arrays;

public class Run {
    public static void main(String[] args) throws FileNotFoundException {


        System.out.println(Arrays.asList(args));

        new Client().main(args);
    }
}
