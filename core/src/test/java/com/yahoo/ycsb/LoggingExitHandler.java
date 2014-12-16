package com.yahoo.ycsb;

public class LoggingExitHandler implements Client.ExitHandler {
    static boolean wasCalled = false;
    @Override
    public void exit() {
        System.out.println("System exit called");
        wasCalled = true;
    }
}
