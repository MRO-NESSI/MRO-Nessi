import pyfli as p

class FLICam(object):
    
    def __init__(self, cam=0):
        self._path = p.FLIList('usb', 'camera')[cam][0]
        self._id = p.FLIOpen(self._path, 'usb', 'camera')
    
    def setExposure(self, time):
        p.setExposureTime(self._id, time)

    def takePicture(self):
        p.exposeFrame(self._id)
        return p.grabFrame(self._id)

    def getTemperature(self):
        return p.getTemperature(self._id)

    def setTemperature(self):
        return p.setTemperature(self._id)

    def __del__(self):
        p.FLIClose(sef._id)
        
