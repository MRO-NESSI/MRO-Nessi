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

    def get_status_update(self):
        """Get the current status of the temperature controller"""
        #send status update request
        self.ser.write('\x90\x04\x01\x00\x50\x01')
        if DEBUG: print 'Status update requested'
        return self.completion()
        
        