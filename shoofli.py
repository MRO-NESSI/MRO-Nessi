#!/usr/bin/python
# -*- coding: utf-8 -*-

#   pyFLI - A Python wrapper for Finger Lakes Instruments scientific cameras
#   Copyright (C) 2012 Luke Schmidt
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ctypes import *
import time
from PIL import Image
import sys

"""Fli class which is meant to provide the Python version of the same
   functions that are defined in the FLI SDK. Since Python does not
   have pass by reference for immutable variables, some of these variables
   are actually stored in the class instance. For example the temperature,
   gain, gainRange, status etc. are stored in the class. """

class Fli:
    def __init__(self):
        #cdll.LoadLibrary("/usr/local/lib/fli/libfli.o")
        self.dll = CDLL("/usr/local/lib/libfli.so")
        error = self.dll.Initialize("/usr/local/lib/")

        cw = c_int()
        ch = c_int()
        self.dll.GetDetector(byref(cw), byref(ch))

        self.width       = cw.value
        self.height      = cw.value
        self.temperature = None
        self.set_T       = None
        self.gain        = None
        self.gainRange   = None
        self.status      = ERROR_CODE[error]
        self.verbosity   = True
        self.preampgain  = None
        self.channel     = None
        self.outamp      = None
        self.hsspeed     = None
        self.vsspeed     = None
        self.serial      = None
        self.exposure    = None
        self.accumulate  = None
        self.kinetic     = None
        
    def __del__(self):
        error = self.dll.ShutDown()
################################################################################
#                           New stuff for FLI                                  #
################################################################################
    def verbose(self, error, function=''):
        if self.verbosity is True:
            print "[%s]: %s" %(function, error)

    def SetVerbose(self, state=True):
        self.verbose = state

    def FLIOpen(self, dev, name, domain):
        """Get a handle to an FLI device. This function requires the ﬁlename and
        domain of the requested device. Valid device ﬁlenames can be obtained using
        the FLIList() function. An application may use any number of handles associated
        with the same physical device. When doing so, it is important to lock the 
        appropriate device to ensure that multiple accesses to the same device 
        do not occur during critical operations."""
        error = self.dll.FLIOpen()
        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
        return ERROR_CODE[error]

    def FLISetDebugLevel(self, host, level):
        """Enable debugging of API operations and communications. Use this function
        in combination with FLIDebug to assist in diagnosing problems that may be
        encountered during programming."""
        pass
    
    def FLIClose(self, dev):
        """Close a handle to a FLI device."""
        pass
    
    def FLIGetLibVersion(self, ver, len):
        """Get the current library version. This function copies up to 'len-1' 
        characters of the current library version string followed by a terminating 
        NULL character into the buffer pointed to by 'ver'."""
        pass
    
    def FLIGetModel(self, dev, model, len):
        """Get the model of a given device. This function copies up to 'len-1' 
        characters of the model string for device 'dev', followed by a terminating 
        NULL character into the buffer pointed to by 'model'."""
        pass
    
    def FLIGetPixelSize(self, dev, pixel_x, pixel_y):
        """Find the dimensions of a pixel in the array of the given device."""
        pass
    
    def FLIGetHWRevision(self, dev, hwrev):
        """Get the hardware revision of a given device."""
        pass
    
    def FLIGetFWRevision(self, dev, fwrev):
        """Get ﬁrmware revision of a given device."""
        pass
    
    def FLIGetArrayArea(self, dev, ul_x, ul_y, lr_x, lr_y):
        """Get the array area of the given camera. This function ﬁnds the total 
        area of the CCD array for camera dev. This area is speciﬁed in terms of 
        a upper-left point and a lower-right point. The upper-left x-coordinate 
        is placed in 'ul_x', the upper-left y-coordinate is placed in 'ul_y', the
        lower-right x-coordinate is placed in 'lr_x', and the lower-right y-coordinate
        is placed in 'lr_y'."""
        pass
    
    def FLIGetVisibleArea(self, dev, ul_x, ul_y, lr_x, lr_y):
        """Get the visible area of the given camera. This function ﬁnds the visible 
        area of the CCD array for the camera 'dev'. This area is speciﬁed in terms
        of a upper-left point and a lower-right point. The upper-left x-coordinate
        is placed in 'ul_x', the upper-left y-coordinate is placed in 'ul_y', the
        lower-right x-coordinate is placed in 'lr_x', the lower-right y-coordinate
        is placed in 'lr_y'."""
        pass
    
    def FLISetExposureTime(self, dev, exptime):
        """Set the exposure time for a camera. This function sets the exposure 
        time for the camera 'dev' to 'exptime' msec."""
        pass
    
    def FLISetImageArea(self, dev, ul_x, ul_y, lr_x, lr_y):
        """Set the image area for a given camera. This function sets the image area
        for camera 'dev' to an area speciﬁed in terms of a upper-left point and a
        lower-right point. The upper-left x-coordinate is 'ul_x', the upper-left
        y-coordinate is 'ul_y', the lower-right x-coordinate is 'lr_x', and the 
        lower-right y-coordinate is 'lr_y'. Note that the given lower-right coordinate
        must take into account the horizontal and vertical bin factor settings,
        but the upper-left coordinate is absolute. In otherwords, the lower-right
        coordinate used to set the image area is a virtual point (lr'_x, lr'_y) 
        determined by:
                        lr'_x = ul_x + (lr_x − ul_x)/hbin
                        lr'_y = ul_y + (lr_y − ul_y)/vbin
        Where (lr'_x, lr'_y) is the coordinate to pass to the 'FLISetImageArea' 
        function, (ul_x, ul_y) and (lr_x, lr_y) are the absolute coordinates of the
        desired image area, 'hbin' is the horizontal bin factor, and 'vbin' is
        the vertical bin factor."""
        pass
    
    def FLISetHBin(self, dev, hbin):
        """Set the horizontal bin factor for a given camera. This function sets 
        the horizontal bin factor for the camera 'dev' to 'hbin'. The valid range
        of the 'hbin' parameter is from 1 to 16."""
        pass
    
    def FLISetVBin(self, dev, vbin):
        """Set the vertical bin factor for a given camera. This function sets the 
        vertical bin factor for the camera 'dev' to 'vbin'. The valid range of the 
        'vbin' parameter is from 1 to 16."""
        pass
    
    def FLISetFrameType(self, dev, frametype):
        """Set the frame type for a given camera. This function sets the frame 
        type for camera 'dev' to 'frametype'. The 'frametype' parameter is either 
        FLI_FRAME_TYPE_NORMAL for a normal frame where the shutter opens or 
        FLI_FRAME_TYPE_DARK for a dark frame where the shutter remains closed."""
        pass
    
    def FLICancelExposure(self, dev):
        """Cancel an exposure for a given camera. This function cancels an 
        exposure in progress by closing the shutter."""
        pass
    
    def FLIGetExposureStatus(self, dev, timeleft):
        """Find the remaining exposure time of a given camera. This function places
        the remaining exposure time (in milliseconds) in the location pointed to 
        by 'timeleft'."""
        pass
    
    def FLISetTemperature(self, dev, temperature):
        """Set the temperature of a given camera. This function sets the temperature 
        of the CCD camera 'dev' to 'temperature' degrees Celsius. The valid range
        of the 'temperature' parameter is from -55C to 45C."""
        pass
    
    def FLIGetTemperature(self, dev, temperature):
        """Get the temperature of a given camera. This function places the temperature
        of the CCD camera cold ﬁnger of device 'dev' in the location pointed to 
        by temperature."""
        pass
    
    def FLIGetCoolerPower(self, dev, power):
        pass
    
    def FLIGrabRow(self, dev, buff, width):
        """Grab a row of an image. This function grabs the next available row of 
        the image from camera device 'dev'. The row of width 'width' is placed 
        in the buffer pointed to by 'buff'. The size of the buffer pointed to by 
        'buff' must take into account the bit depth of the image, meaning the 
        buffer size must be at least 'width' bytes for an 8-bit image, and at least
        2*'width' for a 16-bit image."""
        pass
    
    def FLIExposeFrame(self, dev):
        """Expose a frame for a given camera. This function exposes a frame according
        to the settings (image area, exposure time, bit depth, etc.) of camera 'dev'.
        The settings of 'dev' must be valid for the camera device. They are set by
        calling the appropriate set library functions. This function returns after
        the exposure has started."""
        pass
    
    def FLIFlushRow(self, dev, rows, repeat):
        """Flush rows of a given camera. This function ﬂushes 'rows' rows of camera
        'dev' 'repeat' times."""
        pass
    
    def FLISetNFlushes(self, dev, nflushes):
        """Set the number of ﬂushes for a given camera. This function sets the 
        number of times the CCD array of camera 'dev' is ﬂushed by the FLIExposeFrame 
        before exposing a frame to 'nflushes'. The valid range of the 'nflushes' 
        parameter is from 0 to 16. Some FLI cameras support background ﬂushing.
        Background ﬂushing continuously ﬂushes the CCD eliminating the need for 
        pre-exposure ﬂushing."""
        pass
    
    def FLISetBitDepth(self, dev, bitdepth):
        """Set the gray-scale bit depth for a given camera. This function sets the
        gray-scale bit depth of camera 'dev' to 'bitdepth'. The 'bitdepth' parameter
        is either FLI_MODE_8BIT for 8-bit mode or FLI_MODE_16BIT for 16-bit mode.
        Many cameras do not support this mode."""
        pass
    
    def FLIReadIOPort(self, dev, ioportset):
        """Read the I/O port of a given camera. This function reads the I/O port 
        on camera 'dev' and places the value in the location pointed to by 
        'ioportset'."""
        pass
    
    def FLIWriteIOPort(self, dev, ioportset):
        """Write to the I/O port of a given camera. This function writes the value 
        'ioportset' to the I/O port on camera 'dev'."""
        pass
    
    def FLIConfigureIOPort(self, dev, ioportset):
        """Conﬁgure the I/O port of a given camera. This function conﬁgures the 
        I/O porton camera 'dev' with the value 'ioportset'. The I/O conﬁguration
        of each pin on a given camera is determined by the value of 'ioportset'.
        Setting a respective I/O bit enables the port bit for output while clearing
        an I/O bit enables the port bit for input. By default, all I/O ports are
        conﬁgured as inputs."""
        pass
    
    def FLILockDevice(self, dev):
        """Lock a speciﬁed device. This function establishes an exclusive lock 
        (mutex) on the given device to prevent access to the device by any other
        function or process."""
        pass
    
    def FLIUnlockDevice(self, dev):
        """Unlock a speciﬁed device. This function releases a previously established 
        exclusive lock (mutex) on the given device to allow access to the device
        by any other function or process."""
        pass
    
    def FLIControlShutter(self, dev, shutter):
        """Control the shutter on a given camera. This function controls the 
        shutter function on camera 'dev' according to the 'shutter' parameter. 
        How to control the shutter. A 'shutter' value of FLI_SHUTTER_CLOSE closes 
        the shutter and FLI_SHUTTER_OPEN opens the shutter. 
        FLI_SHUTTER_EXTERNAL_TRIGGER_LOW, FLI_SHUTTER_EXTERNAL_TRIGGER causes the
        exposure to begin only when a logic LOW is detected on I/O port bit 0.
        FLI_SHUTTER_EXTERNAL_TRIGGER_HIGH causes the exposure to begin only when
        a logic HIGH is detected on I/O port bit 0. This setting may not be 
        available on all cameras."""
        pass
    
    def FLIControlBackgroundFlush(self, dev, bgflush):
        """Enables background ﬂushing of CCD array. This function enables the 
        background ﬂushing of the CCD array camera 'dev' according to the 'bgflush'
        parameter. Note that this function may not succeed on all FLI products as
        this feature may not be available. A 'bgflush' value of FLI_BGFLUSH_START
        begins background ﬂushing. It is important to note that background ﬂushing
        is stopped whenever FLIExposeFrame() or FLIControlShutter() are called.
        FLI_BGFLUSH_STOP stops all background ﬂush activity."""
        pass
    
    def FLISetDAC(self, dev, dacset):
        """"""
        pass
        
    def FLIList(self, domain, names):
        """List available devices. This function returns a pointer to a NULL 
        terminated list of device names. The pointer should be freed later with 
        FLIFreeList(). Each device name in the returned list includes the ﬁlename
        needed by FLIOpen(), a separating semicolon, followed by the model name
        or user assigned device name. This is a bitwise combination of interface
        method and devicetype. Validinterfaces include FLIDOMAIN_PARALLEL_PORT,
        FLIDOMAIN_USB, FLIDOMAIN_SERIAL, and FLIDOMAIN_INET. Valid device types
        include FLIDEVICE_CAMERA, FLIDOMAIN_FILTERWHEEL, and FLIDOMAIN_FOCUSER."""
        pass
    
    def FLIFreeList(self, names):
        """Free a previously generated device list. Use this function after 
        FLIList() to free the list of device names."""
        pass
    
    def FLISetFilterPos(self, dev, filter):
        """Set the ﬁlter wheel position of a given device. Use this function to 
        set the ﬁlter wheel position of 'dev' to filter."""
        pass
    
    def FLIGetFilterPos(self, dev, filter):
        """Get the ﬁlter wheel position of a given device. Use this function to 
        get the ﬁlter wheel position of 'dev'."""
        pass
    
    def FLIGetFilterCount(self, dev, filter):
        """Get the ﬁlter wheel ﬁlter count of a given device. Use this function 
        to get the ﬁlter count of ﬁlter wheel 'dev'."""
        pass
    
    def FLIStepMotor(self, dev, steps):
        """Step the ﬁlter wheel or focuser motor of a given device. Use this 
        function to move the focuser or ﬁlter wheel 'dev' by an amount 'steps'."""
        pass
    
    def FLIStepMotorAsync(self, dev, steps):
        """Step the ﬁlter wheel or focuser motor of a given device. Use this 
        function to move the focuser or ﬁlter wheel 'dev' by an amount 'steps'.
        This function is non-blocking."""
        pass
    
    def FLIGetStepperPosition(self, dev, position):
        """Get the stepper motor position of a given device. Use this function to 
        read the stepper motor position of ﬁlter wheel or focuser 'dev'."""
        pass
    
    def FLIGetStepsRemaining(self, dev, steps):
        """Get the number of motor steps remaining. Use this function to determine
        if the stepper motor of 'dev' is still moving."""
        pass
    
    def FLIHomeFocuser(self, dev):
        """Home focuser 'dev'. The home position is closed as far as mechanically
        possible."""
        pass
    
    def FLICreateList(self, domain):
        """Creates a list of all devices within a speciﬁed 'domain'. Use FLIDeleteList()
        to delete the list created with this function. This function is the ﬁrst
        called to begin the iteration through the list of current FLI devices attached."""
        pass
    
    def FLIDeleteList(self):
        """Deletes a list of devices created by FLICreateList()"""
        pass
    
    def FLIListFirst(self, domain, filename, fnlen, name, namelen):
        """Obtains the ﬁrst device in the list. Use this function to get the ﬁrst 
        'domain', 'filename' and 'name' from the list of attached FLI devices created
        using the function FLICreateList(). Use FLIListNext() to obtain more found
        devices."""
        pass
    
    def FLIListNext(self, domain, filename, fnlen, name, namelen):
        """Obtains the next device in the list. Use this function to get the next
        'domain', 'filename' and 'name' from the list of attached FLI devices created
        using the function FLICreateList()."""
        pass
    
    def FLIReadTemperature(self, dev, channel, temperature):
        """Retreive temperature from the FLI focuser 'dev'. Valid channels are
        FLI_TEMPERATURE_INTERNAL and FLI_TEMPERATURE_EXTERNAL."""
        pass
    
    def FLIGetFocuserExtent(self, dev, extent):
        """Retreive the maximum extent for FLI focuser 'dev'"""
        pass
    
    def FLIUsbBulkIO(self, dev, ep, buf, len):
        """"""
        pass
    
    def FLIGetDeviceStatus(self, dev, camera_status):
        """"""
        pass
    
    def FLIGetCameraModeString(self, dev, mode_index, mode_string, siz):
        """"""
        pass
    
    def FLIGetCameraMode(self, dev, mode_index):
        """"""
        pass
    
    def FLISetCameraMode(self, dev, mode_index):
        """"""
        pass
    
#################################################################################    
#    def verbose(self, error, function=''):
#        if self.verbosity is True:
#            print "[%s]: %s" %(function, error)

#    def SetVerbose(self, state=True):
#        self.verbose = state

#    def AbortAcquisition(self):
#        error = self.dll.AbortAcquisition()
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def ShutDown(self):
#        error = self.dll.ShutDown()
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
        
#    def GetCameraSerialNumber(self):
#        serial = c_int()
#        error = self.dll.GetCameraSerialNumber(byref(serial))
#        self.serial = serial.value
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def SetReadMode(self, mode):
#        error = self.dll.SetReadMode(mode)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def SetAcquisitionMode(self, mode):
#        error = self.dll.SetAcquisitionMode(mode)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
        
#    def SetNumberKinetics(self,numKin):
#        error = self.dll.SetNumberKinetics(numKin)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
        
#    def SetNumberAccumulations(self,number):
#        error = self.dll.SetNumberAccumulations(number)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
        
#    def SetAccumulationCycleTime(self,time):
#        error = self.dll.SetAccumulationCycleTime(c_float(time))
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
        
#    def SetKineticCycleTime(self,time):
#        error = self.dll.SetKineticCycleTime(c_float(time))
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def SetShutter(self,typ,mode,closingtime,openingtime):
#        error = self.dll.SetShutter(typ,mode,closingtime,openingtime)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def SetImage(self,hbin,vbin,hstart,hend,vstart,vend):
#        error = self.dll.SetImage(hbin,vbin,hstart,hend,vstart,vend)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def StartAcquisition(self):
#        error = self.dll.StartAcquisition()
#        #self.dll.WaitForAcquisition()
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def GetAcquiredData(self,imageArray):
#        dim = self.width * self.height
#        cimageArray = c_int * dim
#        cimage = cimageArray()
#        error = self.dll.GetAcquiredData(pointer(cimage),dim)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)

#        for i in range(len(cimage)):
#            imageArray.append(cimage[i])

#        self.imageArray = imageArray[:]
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def SetExposureTime(self, time):
#        error = self.dll.SetExposureTime(c_float(time))
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
        
#    def GetAcquisitionTimings(self):
#        exposure   = c_float()
#        accumulate = c_float()
#        kinetic    = c_float()
#        error = self.dll.GetAcquisitionTimings(byref(exposure),byref(accumulate),byref(kinetic))
#        self.exposure = exposure.value
#        self.accumulate = accumulate.value
#        self.kinetic = kinetic.value
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def SetSingleScan(self):
#        self.SetReadMode(4)
#        self.SetAcquisitionMode(1)
#        #self.SetImage(1,1,1,self.width,1,self.height)

#    def SetCoolerMode(self, mode):
#        error = self.dll.SetCoolerMode(mode)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def SaveAsBmp(self, path):
#        im=Image.new("RGB",(512,512),"white")
#        pix = im.load()

#        for i in range(len(self.imageArray)):
#            (row, col) = divmod(i,self.width)
#            picvalue = int(round(self.imageArray[i]*255.0/65535))
#            pix[row,col] = (picvalue,picvalue,picvalue)

#        im.save(path,"BMP")

#    def SaveAsTxt(self, path):
#        file = open(path, 'w')

#        for line in self.imageArray:
#            file.write("%g\n" % line)

#        file.close()

#    def SetImageRotate(self, iRotate):
#        error = self.dll.SetImageRotate(iRotate)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)

#    def SaveAsBmpNormalised(self, path):

#        im=Image.new("RGB",(512,512),"white")
#        pix = im.load()

#        maxIntensity = max(self.imageArray)

#        for i in range(len(self.imageArray)):
#            (row, col) = divmod(i,self.width)
#            picvalue = int(round(self.imageArray[i]*255.0/maxIntensity))
#            pix[row,col] = (picvalue,picvalue,picvalue)

#        im.save(path,"BMP")
        
#    def SaveAsFITS(self, filename, type):
#        error = self.dll.SaveAsFITS(filename, type)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def CoolerON(self):
#        error = self.dll.CoolerON()
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def CoolerOFF(self):
#        error = self.dll.CoolerOFF()
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def IsCoolerOn(self):
#        iCoolerStatus = c_int()
#        error = self.dll.IsCoolerOn(byref(iCoolerStatus))
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return iCoolerStatus.value

#    def GetTemperature(self):
#        ctemperature = c_int()
#        error = self.dll.GetTemperature(byref(ctemperature))
#        self.temperature = ctemperature.value
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def SetTemperature(self,temperature):
#        #ctemperature = c_int(temperature)
#        #error = self.dll.SetTemperature(byref(ctemperature))
#        error = self.dll.SetTemperature(temperature)
#        self.set_T = temperature
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def GetEMCCDGain(self):
#        gain = c_int()
#        error = self.dll.GetEMCCDGain(byref(gain))
#        self.gain = gain.value
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
     
#    def SetEMCCDGainMode(self, gainMode):
#        error = self.dll.SetEMCCDGainMode(gainMode)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]   
        
#    def SetEMCCDGain(self, gain):
#        error = self.dll.SetEMCCDGain(gain)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
        
#    def SetEMAdvanced(self, gainAdvanced):
#        error = self.dll.SetEMAdvanced(gainAdvanced)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def GetEMGainRange(self):
#        low = c_int()
#        high = c_int()
#        error = self.dll.GetEMGainRange(byref(low),byref(high))
#        self.gainRange = (low.value, high.value)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
      
#    def GetNumberADChannels(self):
#        noADChannels = c_int()
#        error = self.dll.GetNumberADChannels(byref(noADChannels))
#        self.noADChannels = noADChannels.value
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def GetBitDepth(self):
#        bitDepth = c_int()

#        self.bitDepths = []

#        for i in range(self.noADChannels):
#            self.dll.GetBitDepth(i,byref(bitDepth))
#            self.bitDepths.append(bitDepth.value)

#    def SetADChannel(self, index):
#        error = self.dll.SetADChannel(index)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        self.channel = index
#        return ERROR_CODE[error]  
        
#    def SetOutputAmplifier(self, index):
#        error = self.dll.SetOutputAmplifier(index)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        self.outamp = index
#        return ERROR_CODE[error]
        
#    def GetNumberHSSpeeds(self):
#        noHSSpeeds = c_int()
#        error = self.dll.GetNumberHSSpeeds(self.channel, self.outamp, byref(noHSSpeeds))
#        self.noHSSpeeds = noHSSpeeds.value
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def GetHSSpeed(self):
#        HSSpeed = c_float()

#        self.HSSpeeds = []

#        for i in range(self.noHSSpeeds):
#            self.dll.GetHSSpeed(self.channel, self.outamp, i, byref(HSSpeed))
#            self.HSSpeeds.append(HSSpeed.value)
            
#    def SetHSSpeed(self, index):
#        error = self.dll.SetHSSpeed(index)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        self.hsspeed = index
#        return ERROR_CODE[error]
        
#    def GetNumberVSSpeeds(self):
#        noVSSpeeds = c_int()
#        error = self.dll.GetNumberVSSpeeds(byref(noVSSpeeds))
#        self.noVSSpeeds = noVSSpeeds.value
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def GetVSSpeed(self):
#        VSSpeed = c_float()

#        self.VSSpeeds = []

#        for i in range(self.noVSSpeeds):
#            self.dll.GetVSSpeed(i,byref(VSSpeed))
#            self.preVSpeeds.append(VSSpeed.value)

#    def SetVSSpeed(self, index):
#        error = self.dll.SetVSSpeed(index)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        self.vsspeed = index
#        return ERROR_CODE[error] 
    
#    def GetNumberPreAmpGains(self):
#        noGains = c_int()
#        error = self.dll.GetNumberPreAmpGains(byref(noGains))
#        self.noGains = noGains.value
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def GetPreAmpGain(self):
#        gain = c_float()

#        self.preAmpGain = []

#        for i in range(self.noGains):
#            self.dll.GetPreAmpGain(i,byref(gain))
#            self.preAmpGain.append(gain.value)

#    def SetPreAmpGain(self, index):
#        error = self.dll.SetPreAmpGain(index)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        self.preampgain = index
#        return ERROR_CODE[error]

#    def SetTriggerMode(self, mode):
#        error = self.dll.SetTriggerMode(mode)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#    def GetStatus(self):
#        status = c_int()
#        error = self.dll.GetStatus(byref(status))
#        self.status = ERROR_CODE[status.value]
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
        
#    def GetSeriesProgress(self):
#        acc = c_long()
#        series = c_long()
#        error = self.dll.GetAcquisitionProgress(byref(acc),byref(series))
#        if ERROR_CODE[error] == "DRV_SUCCESS":
#            return series.value
#        else:
#            return None
             
#    def GetAccumulationProgress(self):
#        acc = c_long()
#        series = c_long()
#        error = self.dll.GetAcquisitionProgress(byref(acc),byref(series))
#        if ERROR_CODE[error] == "DRV_SUCCESS":
#            return acc.value
#        else:
#            return None
        
#    def SetFrameTransferMode(self, frameTransfer):
#        error = self.dll.SetFrameTransferMode(frameTransfer)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
        
#    def SetShutterEx(self, typ, mode, closingtime, openingtime, extmode):
#        error = self.dll.SetShutterEx(typ, mode, closingtime, openingtime, extmode)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]
        
#    def SetSpool(self, active, method, path, framebuffersize):
#        error = self.dll.SetSpool(active, method, c_char_p(path), framebuffersize)
#        self.verbose(ERROR_CODE[error], sys._getframe().f_code.co_name)
#        return ERROR_CODE[error]

#ERROR_CODE = {
#    20001: "DRV_ERROR_CODES",
#    20002: "DRV_SUCCESS",
#    20003: "DRV_VXNOTINSTALLED",
#    20006: "DRV_ERROR_FILELOAD",
#    20007: "DRV_ERROR_VXD_INIT",
#    20010: "DRV_ERROR_PAGELOCK",
#    20011: "DRV_ERROR_PAGE_UNLOCK",
#    20013: "DRV_ERROR_ACK",
#    20024: "DRV_NO_NEW_DATA",
#    20026: "DRV_SPOOLERROR",
#    20034: "DRV_TEMP_OFF",
#    20035: "DRV_TEMP_NOT_STABILIZED",
#    20036: "DRV_TEMP_STABILIZED",
#    20037: "DRV_TEMP_NOT_REACHED",
#    20038: "DRV_TEMP_OUT_RANGE",
#    20039: "DRV_TEMP_NOT_SUPPORTED",
#    20040: "DRV_TEMP_DRIFT",
#    20050: "DRV_COF_NOTLOADED",
#    20053: "DRV_FLEXERROR",
#    20066: "DRV_P1INVALID",
#    20067: "DRV_P2INVALID",
#    20068: "DRV_P3INVALID",
#    20069: "DRV_P4INVALID",
#    20070: "DRV_INIERROR",
#    20071: "DRV_COERROR",
#    20072: "DRV_ACQUIRING",
#    20073: "DRV_IDLE",
#    20074: "DRV_TEMPCYCLE",
#    20075: "DRV_NOT_INITIALIZED",
#    20076: "DRV_P5INVALID",
#    20077: "DRV_P6INVALID",
#    20083: "P7_INVALID",
#    20089: "DRV_USBERROR",
#    20091: "DRV_NOT_SUPPORTED",
#    20099: "DRV_BINNING_ERROR",
#    20990: "DRV_NOCAMERA",
#    20991: "DRV_NOT_SUPPORTED",
#    20992: "DRV_NOT_AVAILABLE"
#}
