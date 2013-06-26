from time import sleep
from threading import Lock
import pyfli as p

class FLICam(object):
    """Represents an FLI USB Camera."""

    def __init__(self, cam=0):
        self._path = p.FLIList('usb', 'camera')[cam][0]
        self._id   = p.FLIOpen(self._path, 'usb', 'camera')
        self.lock  =  Lock()
    
    def setExposure(self, time):
        with self.lock:
            p.setExposureTime(self._id, time)

    def takePicture(self):
        with self.lock:
            p.exposeFrame(self._id)
            wait = 100
            while wait != 0:
                wait = p.getExposureStatus(self._id)
                sleep(wait/1000)
            return p.grabFrame(self._id)

    def getTemperature(self):
        with self.lock:
            return p.getTemperature(self._id)

    def setTemperature(self, temp):
        with self.lock:
            return p.setTemperature(self._id, temp)

    def setBinning(self, hBin, vBin):
        with self.lock:
            p.setHBin(self._id, hBin)
            p.setVBin(self._id, vBin)
        
    def __del__(self):
        with self.lock:
            p.FLIClose(sef._id)
        
