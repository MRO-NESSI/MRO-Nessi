#!/usr/bin/env python

import serial
import time
import sys

DEBUG = True

class tlabs:
    """Represents the Thorlabs TDC001 controller."""
    
    def __init__(self, port='/dev/ttyUSB0'):
        """Performs necessary startup procedures."""
        self.__port = port

        # Establish a connection to the KMtronic relay board
        self.ser = serial.Serial(port=self.__port, baudrate=115200, bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                                 timeout=1, rtscts=True)
        
    def __del__(self):
        """Perform cleanup operations."""
        self.ser.close()

    def flash(self):
        """Flash light on front."""
        self.ser.write('\x23\x02\x00\x00\x50\x01')
        if DEBUG: print "DEBUG: Flash"

        return True
    
    def home(self):
        """Home stage."""
        self.ser.write('\x43\x04\x01\x00\x50\x01')
        if DEBUG: print "DEBUG: Home Stage"
        now = time.time()
        while True:
            ch = self.ser.read(self.ser.inWaiting())
            if DEBUG: 
                if ch != '': 
                    print 'ch is:', ch, sys.getsizeof(ch) #prints size in bytes
            if time.time() > now+30.0:
                break
            