package com.yahoo.ycsb;

public class LoggingExitHandler implements Client.ExitHandler {

    @Override
    public void exit() {
        System.out.println("System exit called");
    }
}
