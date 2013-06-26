import serial
from serial import SerialException, SerialTimeoutException

from instrument import InstrumentComponent, InstrumentError

class LakeshoreController(InstrumentComponent):
    """Represents the Lakeshore 336 Temperature Controller."""
    
    temp_probes = {
        'a':'Radiation Shield',
        'b':'Filter Wheels',
        'c':'Mask Wheel',
        'd':'FPA',
        }

    def __init__(
        self, instrument, temp_probes = {
            'a':'Radiation Shield',
            'b':'Filter Wheels'   ,
            'c':'Mask Wheel'      ,
            'd':'FPA'             ,
            }
        ):
        """Sets up component, and connects to the Lakeshore controller.
        
        Arguments:
            instrument  -- Copy of the NESSI instrument.
            temp_probes -- Dictionary mapping probe character to name.
        Raises:
            InstrumentError

        """
        super(LakeshoreController, self).__init__(instrument)

        self.temp_probes = temp_probes
        self.__port = '/dev/ttylakeshore'

        #Open serial connection
        try:
            self.ser    = serial.Serial(port = self.__port, 
                                        baudrate = 57600,
                                        bytesize = serial.SEVENBITS,
                                        parity = serial.PARITY_ODD,
                                        stopbits = serial.STOPBITS_ONE,
                                        timeout=1)
        except ValueError as e:
            msg  = 'Lakeshore Serial call has a programming error in it.\n'
            msg += 'The following ValueError was raised...\n'
            msg += repr(e)
            raise InstrumentError(msg)

        except SerialException as e:
            msg  = 'Lakeshore was unable to connect...\n'
            msg += 'The following SerialException was raised...\n'
            msg += repr(e)
            raise InstrumentError(msg)
            
        except Exception as e:
            raise InstrumentError('An unknown error occurred!\n %s' 
                                  % repr(e))


    def __del__(self):
        """Perform cleanup operations."""
        self.ser.close()
        
    def _completion(self):
        """Generic function that waits to read a completion command."""
        with self.lock:
            while True:
                ch = self.ser.readline()
                if ch != '': 
                    break
        return ch

    def _identify(self):
        """Get the current status of the temperature controller"""
        try:
            with self.lock:
                self.ser.write('*IDN?\n')
        except SerialTimeoutException:
            self.ser.close()
            raise InstrumentError('Writing to Lakeshore controller timed'
                                  ' out. Has it been powered off or '
                                  'disconnected?\n Closed connection to'
                                  ' Lakeshore controller...')

        return self._completion()
    
    def get_temp(self, port):
        """Get the temperature at the given port.
        
        Arguments:
            port -- Character representing which port to read.
                    'a'/'b'/'c'/'d' are the only valid options.

        Raises:
            InstrumentError

        returns String representing temperature at the given port, 
                in kelvin.
        """
        if port not in ['a', 'b', 'c', 'd']:
            raise InstrumentError('A programming error attempted to read'
                                  'a non-existent port on the Lakeshore'
                                  'temperature controller!')
        try:
            with self.lock:
                self.ser.write('KRDG?' + port + '\n')
        except SerialTimeoutException:
            self.ser.close()
            raise InstrumentError('Writing to Lakeshore controller timed'
                                  ' out. Has it been powered off or '
                                  'disconnected?\n Closed connection to'
                                  ' Lakeshore controller...')

        return self._completion()

    def kill(self):
        """Closes connection. Called by a kill_all"""
        self.ser.close()

