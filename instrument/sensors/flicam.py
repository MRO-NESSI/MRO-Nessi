from time import sleep

import pyfli as p

from instrument.component import InstrumentComponent, InstrumentError

class FLICam(InstrumentComponent):
    """Represents an FLI USB Camera."""

    def __init__(self, instrument, cam=0):
        """Connects to a new FLI Camera. 

        Arguments:
            instrument -- Copy of the NESSI instrument
            cam        -- int representing which camera to use
                          (defaults to 0).

        Raises InstrumentError
        """

        super(FLICam, self).__init__(instrument)

        try:
            self._path = p.FLIList('usb', 'camera')[cam][0]
            self._id   = p.FLIOpen(self._path, 'usb', 'camera')
        except Exception as e:
            raise InstrumentError('An error occurred initializing the'
                                  ' Guide cam. Is it plugged in and'
                                  ' powered on.\n The following error'
                                  ' was raised...\n %s' % repr(e))
    
    def setExposure(self, time):
        """Sets the exposure time of the FLI Camera.

        Arguments:
            time --- new exposure time

        Raises:
            InstrumentError
        
        returns None
        """
        try:
            with self.lock:
                p.setExposureTime(self._id, time)
        except Exception as e:
            raise InstrumentError('An error occured communicating with the'
                                  ' guide cam!\n The following error was'
                                  ' raised...\n %s' % repr(e))

    def takePicture(self):
        """Takes a picture with the guide cam.

        Arguments:

        Raises:
            InstrumentError
        
        returns numpy array of image
        """

        try:
            with self.lock:
                p.exposeFrame(self._id)
                wait = 100
                while wait != 0:
                    wait = p.getExposureStatus(self._id)
                    sleep(wait/1000)
        except Exception as e:
            raise InstrumentError('An error occured communicating with the'
                                  ' guide cam!\n The following error was'
                                  ' raised...\n %s' % repr(e))
            
        return p.grabFrame(self._id)

    def getTemperature(self):
        """Returns the temperature of the FLI Camera.

        Arguments:
        
        Raises:
            InstrumentError
        
        returns string representation of the temperature, in Celsius.
        """
        try:
            with self.lock:
                return p.getTemperature(self._id)
        except Exception as e:
            raise InstrumentError('An error occured communicating with the'
                                  ' guide cam!\n The following error was'
                                  ' raised...\n %s' % repr(e))
            
    def setTemperature(self, temp):
        """Set the temperature of the FLI Camera.

        Arguments:
            temp -- new temperature of the camera, in Celsius

        Raises:
            InstrumentError

        returns whatever pyfli.setTeperature returns... ?
        """
        try:
            with self.lock:
                return p.setTemperature(self._id, temp)
        except Exception as e:
            raise InstrumentError('An error occured communicating with the'
                                  ' guide cam!\n The following error was'
                                  ' raised...\n %s' % repr(e))           

    def setBinning(self, hBin, vBin):
        """Set the binning of the FLI Camera.
        
        Arguments:
            hBin  -- horizontal binning
            vBin  -- vertical binning

        Raises:
            InstrumentError

        returns None
        """
        try:
            with self.lock:
                p.setHBin(self._id, hBin)
                p.setVBin(self._id, vBin)
        except Exception as e:
            raise InstrumentError('An error occured communicating with the'
                                  ' guide cam!\n The following error was'
                                  ' raised...\n %s' % repr(e))           
        
    def __del__(self):
        with self.lock:
            p.FLIClose(self._id)

    def kill(self):
        """Closes connection. Called by a kill_all"""
        p.FLIClose(self._id)
        
