package com.yahoo.ycsb.db;

import com.yahoo.ycsb.Client;

import java.io.FileNotFoundException;

public class RunYcsb {
    public static void main(String[] args) throws FileNotFoundException {
        new Client().main(args);
    }
}
