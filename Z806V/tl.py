#!/usr/bin/env python
import serial
from struct import pack, unpack
import sys

from handlers import *

DEBUG = True

class TLabs:
    """Represents a Thorlabs TDC001 controller."""
    
    commands = { 
        #COMMAND          #SIGNAL HEADER           #Has exit status
        'Identify'     : ('\x23\x02\x00\x00\x50\x01',         False), 
        'Home'         : ('\x43\x04\x01\x00\x50\x01',         True), 
        'Status'       : ('\x90\x04\x01\x00\x50\x01',         True), 
        'Move Absolute': ('\x48\x04\x06\x00\x50\x01\x01\x00', True),
        'Move Relative': ('\x48\x04\x06\x00\x50\x01\x01\x00', True),
    }
    ports = {0: '/dev/ttyREI12', 1: '/dev/ttyREI34'}

    def __init__(self, port=0):
        """Build controller, and establish connection."""
        try:
            self.__port = TLabs.ports[port]
        except:
            raise InvalidPortException()
        # Establish a connection to the KMtronic relay board
        self.ser = serial.Serial(port=self.__port, baudrate=115200,
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 timeout=1, rtscts=True)
        
    def __del__(self):
        """Perform cleanup operations."""
        self.ser.close()

    def read_exit_status(self):
        """Reads exit status from controller.

        Generic function to read from the serial port.
        Reads untill an empty line is read.

        returns (hex, characters)
        """
        """
        TODO: This only returns one line. It may need to be
        examined
        """
        while True:
            ch = self.ser.readline()
            if ch != '': 
                break
        ch = ch.encode('hex')
        return [ch[i] + ch[i+1] for i in range(0,len(ch)-1,2)]
    
    

    def send_command(self, command):
        """Send a command to the controller.
        
        returns the exit status, if the command returns one. Otherwise
        none.
        """
        command = TLabs.commands[command]
        self.ser.write(command[0])
        return self.read_exit_status() if command[1] else None
            
    def move_relative(self,distance=0):
        """Move the stage a relative distance.  

        distance --- in microns (signed int)
        
        returns exit status.
        """
        """
        Conversion factors:
          34,304 (encoder counts)/(revolution of lead screw) 
          29 (nm)/(encoder count)
        The command expects input in encoder counts.
        """
        #get current position to make sure move doesn't drive to limit
        #TODO:IS THAT NECESSARY?
        #convert distance in um to counts, make sure it is an integer.
        intcounts = int(distance / 0.02915111) #um per count
        #convert to hex
        counts = pack('<l', intcounts)
        if DEBUG: print counts
        #write move command
        self.ser.write('\x48\x04\x06\x00\xd0\x01\x00\x01' + counts)
        if DEBUG: print 'Start relative move by: ', intcounts, ' counts, ', distance, 'um.'
        #wait for completion command
        return self.read_exit_status()
        
    def move_absolute(self,position=0):
        """Move the stage an absolute position.

        postition --- in microns (signed int)
        
        returns exit status.
        """
        """
        Conversion factors:
          34,304 (encoder counts)/(revolution of lead screw) 
          29 (nm)/(encoder count)
        The command expects input in encoder counts.
        """
        #convert distance in um to counts, make sure it is an integer.
        intcounts = int(position / 0.02915111) #um per count
        #convert to hex
        counts = pack('>L', intcounts)
        if DEBUG: print counts
        #write move command
        self.ser.write('\x53\x04\x06\x00\x50\x01\x01\x00' + counts)
        if DEBUG: print 'Start absolute move to: ', position, 'um.'
        #wait for completion command
        return self.read_exit_status()
