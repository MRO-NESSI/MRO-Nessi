#!/usr/bin/env python
import serial
from serial import SerialException, SerialTimeoutException
from struct import pack, unpack

from instrument.component import InstrumentComponent, InstrumentError, logCall

class ThorlabsController(InstrumentComponent):
    """Represents a Thorlabs TDC001 controller."""

    #TX Header Info
    _source     = '\x01'
    _dest       = '\x50'
    _dest_ord   = '\xd0'    #_dest | 0x80
    _channel    = '\x01'
    _chan_ident = '\x01\x00'
    
    _ports = {1: '/dev/ttyAGR', 0: '/dev/ttyREI34'}

    def __init__(self, instrument, port):
        """Build controller, and establish connection.
        
        Arguments:
            instrument -- Copy of the NESSI instrument
            port       -- Which controller to connect to. Only 0 or 1
                          is valid
        
        Raises:
            InstrumentError
        """

        super(ThorlabsController, self).__init__(instrument)

        if port not in [0,1]: 
            raise InstrumentError('A programming error attempted to'
                                  ' access a non-existent Thorlabs '
                                  'controller!')
        self.__port = ThorlabsController._ports[port]
        self._name  = self.__port[3:].upper()
        
        try:
            self.ser = serial.Serial(port=self.__port, baudrate=115200,
                                     bytesize=serial.EIGHTBITS,
                                     parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE,
                                     timeout=1, rtscts=True)
        except ValueError as e:
            msg  = 'Thorlabs Serial call has a programming error in it.\n'
            msg += 'The following ValueError was raised...\n'
            msg += repr(e)
            raise InstrumentError(msg)

        except SerialException as e:
            msg  = 'Thorlabs was unable to connect...\n'
            msg += 'The following SerialException was raised...\n'
            msg += repr(e)
            raise InstrumentError(msg)
            
        except Exception as e:
            raise InstrumentError('An unknown error occurred!\n %s' 
                                  % repr(e))


    def __del__(self):
        """Perform cleanup operations."""
        self.ser.close()

    def kill(self):
        self.ser.close()

    def __str__(self):
        return 'Thorlabs controller: %s' % self._name

    def _read_exit_status(self):
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
        """Flash motor controller.
        
        Arguments:
        Raises:
            InstrumentError
        return None
        """
        """
        See MGMSG_MOD_IDENTIFY
        Page 19 - APT_Communications_Protocol_Rev 6
        """

        tx  = '\x23\x02\x00\x00' + ThorlabsController._dest 
        tx += ThorlabsController._source
        with self.lock:
            try:
                self.ser.write(tx)
            except SerialTimeoutException:
                self.ser.close()
                raise InstrumentError('Writing to Thorlab controller timed'
                                      ' out. Has it been powered off or '
                                      'disconnected?\n Closed connection to'
                                      ' Thorlab controller...')
            
    @logCall(msg='Homeing Thorlabs')
    def home(self):
        """Home the motor.
        Arguments:
        Raises:
            InstrumentError
        return an exit string of little-endian bytes.
        """
        """
        See MGMSG_MOT_MOVE_HOME
        Page 50 - APT_Communications_Protocol_Rev 6
        """
        
        tx  = '\x43\x04' + ThorlabsController._channel + '\x00'
        tx += ThorlabsController._dest + ThorlabsController._source

        with self.lock:
            try:
                self.ser.write(tx)
                return self._read_exit_status()
            except SerialException:
                self.ser.close()
                raise InstrumentError('Writing to Thorlab controller timed'
                                      ' out. Has it been powered off or '
                                      'disconnected?\n Closed connection to'
                                      ' Thorlab controller...')

        position = self.position

        self.instrument.keywords[self._name] = position
                     

    @property
    def position(self):
        """Returns the position of actuator."""
        return self.status()['Position']


    def status(self):
        """Returns the status of the motor.
        
        Arguments:
        Raises:
            InstrumentError
        return a dictionary of a number of status messages.
        """
        """
        See MGMSG_MOT_REQ_DCSTATUSUPDATE
        Page 91 - APT_Communications_Protocol_Rev 6
        """

        tx  = '\x90\x04' + ThorlabsController._channel + '\x00' 
        tx += ThorlabsController._dest + ThorlabsController._source

        with self.lock:
            try:
                self.ser.write(tx)
                stat_string = self._read_exit_status()[1]
            except SerialTimeoutException:
                self.ser.close()
                raise InstrumentError('Writing to Thorlab controller timed'
                                      ' out. Has it been powered off or '
                                      'disconnected?\n Closed connection to'
                                      ' Thorlab controller...')
        stat = {}
        stat['Chan Ident'], stat['Position'], stat['Velocity'], \
            _ , stat['Status Bits'] = unpack('<HlHHI', stat_string[6:])
        
        stat['Position'] = stat['Position'] * 0.02915111
        return stat

    @logCall(msg='Moving Thorlabs')
    def move_relative(self, distance):
        """Move the stage a relative distance.  

        Arguments:
            distance -- in microns (signed int)
        Raises:
            InstrumentError
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

        #convert distance in um to counts, make sure it is an integer.
        intcounts = round(distance / 0.02915111) #um per count
        #convert to hex
        counts = pack('<l', intcounts)

        tx  = '\x48\x04\x06\x00' + ThorlabsController._dest_ord 
        tx += ThorlabsController._source + ThorlabsController._chan_ident
        tx += counts
            
        with self.lock:
            try:
                self.ser.write(tx)
                return self._read_exit_status()
            except SerialTimeoutException:
                self.ser.close()
                raise InstrumentError('Writing to Thorlab controller timed'
                                      ' out. Has it been powered off or '
                                      'disconnected?\n Closed connection to'
                                      ' Thorlab controller...')

        position = self.position

        self.instrument.keywords[self._name] = position

    @logCall(msg='Moving Thorlabs')
    def move_absolute(self, position):
        """Move the stage an absolute position.

        Arguments:
            position -- in microns (signed int)
        Raises:
            InstrumentError
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

        #convert distance in um to counts, make sure it is an integer.
        intcounts = round(position / 0.02915111) #um per count
        #convert to hex
        counts = pack('<l', intcounts)

        tx  = '\x53\x04\x06\x00' + ThorlabsController._dest_ord 
        tx += ThorlabsController._source + ThorlabsController._chan_ident
        tx += counts

        with self.lock:
            try:
                self.ser.write(tx)
                return self._read_exit_status()
            except SerialTimeoutException:
                self.ser.close()
                raise InstrumentError('Writing to Thorlab controller timed'
                                      ' out. Has it been powered off or '
                                      'disconnected?\n Closed connection to'
                                      ' Thorlab controller...')
        position = self.position

        self.instrument.keywords[self._name] = position
