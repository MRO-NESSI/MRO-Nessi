#!/usr/bin/env python
import serial
from struct import pack, unpack
from threading import Lock

def run_async(func):
    from threading import Thread
    from functools import wraps

    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target = func, args = args, kwargs = kwargs)
        func_hl.start()
        return func_hl

    return async_func


class TLabs:
    """Represents a Thorlabs TDC001 controller."""

    #TX Header Info
    _source     = '\x01'
    _dest       = '\x50'
    _dest_ord   = '\xd0'    #_dest | 0x80
    _channel    = '\x01'
    _chan_ident = '\x01\x00'
    
    _ports = {0: '/dev/ttyREI12', 1: '/dev/ttyREI34'}

    def __init__(self, port=0):
        """Build controller, and establish connection."""
        try:
            self.__port = TLabs._ports[port]
        except:
            raise InvalidPortException()
        # Establish a connection to the KMtronic relay board
        self.ser = serial.Serial(port=self.__port, baudrate=115200,
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 timeout=1, rtscts=True)
        self.lock = Lock()
        
    def __del__(self):
        """Perform cleanup operations."""
        self.ser.close()

    def read_exit_status(self):
        """Reads exit status from controller.

        Generic function to read from the serial port.
        Returns the first non-empty line

        returns an array of bytes, little-endian.
        """
        while True:
            l = self.ser.readline()
            if l != '': 
                break
        h = l.encode('hex')
        return [h[i] + h[i+1] for i in range(0,len(h)-1,2)], l

    def identify(self):
        """Flash motor controller."""
        """
        See MGMSG_MOD_IDENTIFY
        Page 19 - APT_Communications_Protocol_Rev 6
        """
        tx = '\x23\x02\x00\x00' + TLabs._dest + TLabs._source
        self.ser.write(tx)
        return
    
    def home(self):
        """Home the motor."""
        """
        See MGMSG_MOT_MOVE_HOME
        Page 50 - APT_Communications_Protocol_Rev 6
        """
        with self.lock:
            tx = '\x43\x04' + TLabs._channel + '\x00' + TLabs._dest + TLabs._source
            self.ser.write(tx)
            return self.read_exit_status()

    def status(self):
        """Returns the status of the motor."""
        """
        See MGMSG_MOT_REQ_DCSTATUSUPDATE
        Page 91 - APT_Communications_Protocol_Rev 6
        """
        with self.lock:
            tx = '\x90\x04' + TLabs._channel + '\x00' + TLabs._dest + TLabs._source
            self.ser.write(tx)
            stat_string = self.read_exit_status()[1]
            stat = {}
            stat['Chan Ident'], stat['Position'], stat['Velocity'], _ ,stat['Status Bits'] \
                = unpack('<HlHHI', stat_string[6:])
            stat['Position'] = stat['Position'] * 0.02915111
            return stat

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

        See MGMSG_MOT_MOVE_RELATIVE
        Page 51 - APT_Communications_Protocol_Rev 6
        """
        with self.lock:
        #convert distance in um to counts, make sure it is an integer.
            intcounts = round(distance / 0.02915111) #um per count
        #convert to hex
            counts = pack('<l', intcounts)
            tx = '\x48\x04\x06\x00' + TLabs._dest_ord + TLabs._source
            tx = tx + TLabs._chan_ident + counts
            self.ser.write(tx)
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

        See MGMSG_MOT_MOVE_ABSOLUTE
        Page 54 - APT_Communications_Protocol_Rev 6
        """
        with self.lock:
        #convert distance in um to counts, make sure it is an integer.
            intcounts = round(position / 0.02915111) #um per count
        #convert to hex
            counts = pack('<l', intcounts)
        #write move command
            tx = '\x53\x04\x06\x00' + TLabs._dest_ord + TLabs._source
            tx = tx + TLabs._chan_ident + counts
            self.ser.write(tx)
            return self.read_exit_status()
    
class InvalidPortException(Exception):
    def __init__(self, value = 'Port not valid'):
        self.value = value
    def __str__(self):
        return repr(self.value)

if __name__ == '__main__':
    #Init Motors
    m1 = TLabs(port=0)
    m2 = TLabs(port=1)

    #m1
    print 'Test port 0...'
    m1.identify()
    print 'Port 0 is flashing...'
    print 'Hit ENTER when confirmed...'
    raw_input()
    print 'm1 is homing...'
    m1.home()
    print 'Hit ENTER when confirmed...'
    raw_input()

    #m2
    print 'Test port 1...'
    m2.identify()
    print 'Port 1 is flashing...'
    print 'Hit ENTER when confirmed...'
    raw_input()
    print 'm2 is homing...'
    m2.home()
    print 'Hit ENTER when confirmed...'
    raw_input()
    
    
