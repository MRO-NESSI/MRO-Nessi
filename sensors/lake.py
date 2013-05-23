#!/usr/bin/env python

import serial
import time
import sys
from struct import pack, unpack

DEBUG = True

class tc:
    """Represents the Lakeshore 336 Temperature Controller."""
    
    def __init__(self):
        """Performs necessary startup procedures."""
        self.__port = '/dev/ttylakeshore'
        # Establish a connection to the KMtronic relay board
        self.ser = serial.Serial(port=self.__port, baudrate=57600, bytesize=serial.SEVENBITS,
                                 parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_ONE,
                                 timeout=1)
        
    def __del__(self):
        """Perform cleanup operations."""
        self.ser.close()
        
    def completion(self):
        """Generic function that waits to read a completion command."""
        while True:
            ch = self.ser.readline()
            if ch != '': 
                break
        return ch

    def identify(self):
        """Get the current status of the temperature controller"""
        #send identify request
        self.ser.write('*IDN?\n')
        if DEBUG: print 'Identify Device:'
        return self.completion()
    
    def kelvin(self,port='a'):
        """Get the current temps in Kelvin."""
        self.ser.write('KRDG?' + port + '\n')
        if DEBUG: print 'Return Kelvin:'
        return self.completion()
        
        