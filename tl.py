#!/usr/bin/env python

import serial
import time
import sys
from struct import pack, unpack

DEBUG = True

class tlabs:
    """Represents the Thorlabs TDC001 controller."""
    
    def __init__(self, port=0):
        """Performs necessary startup procedures."""
        if port == 0:
            self.__port = '/dev/ttyREI12'
        if port == 1:
            self.__port = '/dev/ttyREI34'
        # Establish a connection to the KMtronic relay board
        self.ser = serial.Serial(port=self.__port, baudrate=115200, bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                                 timeout=1, rtscts=True)
        
    def __del__(self):
        """Perform cleanup operations."""
        self.ser.close()

    def identify(self):
        """Flash light on front."""
        self.ser.write('\x23\x02\x00\x00\x50\x01')
        if DEBUG: print "DEBUG: Flash"
    
    def completion(self):
        """Generic function that waits to read a completion command such as, home
        finished, move complete, etc."""
        now = time.time()
        while True:
            ch = self.ser.readline()
            if ch != '': 
                break
        
        return ch.encode('hex'), ch
    
    def home(self):
        """Home stage."""
        self.ser.write('\x43\x04\x01\x00\x50\x01')
        if DEBUG: print 'DEBUG: Home Stage'
        return self.completion()
            
    def move_relative(self,distance=0):
        """Move the stage a relative distance.  Input is in microns, signed integer.
        The conversion factor is:  34,304 encoder counts/revolution of lead screw, 
        which moves the lead screw by 1mm, or 1mm/34,304 counts = 29nm/encoder count.
        The command expects input in encoder counts."""
        #get current position to make sure move doesn't drive to limit
        
        #if relative move will place it at a limit, move to just before the limit
        
        #convert distance in um to counts, make sure it is an integer.
        intcounts = int(distance / 0.02915111) #um per count
        #convert to hex
        counts = pack('<L', intcounts)
        if DEBUG: print str(counts)
        #write move command
        self.ser.write('\x48\x04\x06\x00\x50\x01\x01\x00' + counts)
        if DEBUG: print 'Start relative move by: ', intcounts, ' counts, ', distance, 'um.'
        #wait for completion command
        return self.completion()  
        
    def move_absolute(self,position=0):
        """Move the stage to an absolute position.  Input is in microns, signed integer.
        The conversion factor is:  34,304 encoder counts/revolution of lead screw, 
        which moves the lead screw by 1mm, or 1mm/34,304 counts = 29nm/encoder count.
        The command expects input in encoder counts."""
        #convert distance in um to counts, make sure it is an integer.
        intcounts = int(position / 0.02915111) #um per count
        #convert to hex
        counts = pack('<L', intcounts)
        if DEBUG: print counts
        #write move command
        self.ser.write('\x53\x04\x06\x00\x50\x01\x01\x00' + counts)
        if DEBUG: print 'Start absolute move to: ', position, 'um.'
        #wait for completion command
        return self.completion()
        
    def get_status_update(self):
        """Get the current status of the actuator, including position, encoder count,
        and other status messages, such as limit switch activated, in motion, etc."""
        #send status update request
        self.ser.write('\x90\x04\x01\x00\x50\x01')
        if DEBUG: print 'Status update requested'
        status = self.completion()
        #format the status as a dictionary
        
        #return the dictionary    
        return status
        
        
