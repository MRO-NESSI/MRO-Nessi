#!/usr/bin/env python

import serial
import time
import sys

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
            ch = self.ser.read(self.ser.inWaiting())
            if DEBUG: 
                if ch != '': 
                    print 'ch is:', ch, sys.getsizeof(ch) #prints size in bytes
            if time.time() > now+30.0:
                break
    
    def home(self):
        """Home stage."""
        self.ser.write('\x43\x04\x01\x00\x50\x01')
        if DEBUG: print "DEBUG: Home Stage"
        self.completion(self)
            
    def move_relative(self,distance=0):
        """Move the stage a relative distance.  Input is in microns, signed integer.
        The conversion factor is:  34,304 encoder counts/revolution of lead screw, 
        which moves the lead screw by 1mm, or 1mm/34,304 counts = 29nm/encoder count.
        The command expects input in encoder counts."""
        #convert distance in um to counts, make sure it is an integer.
        counts = int(distance * 0.02915111) #um per count
        #convert to hex
        
        #convert to input format, least sig digit first
        
        #write move command
        if DEBUG: print 'Start relative move by: ', counts, ' counts.'
        #wait for completion command
        self.completion(self)    