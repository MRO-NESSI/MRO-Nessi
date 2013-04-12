#!/usr/bin/env python
"""Guider connects getim.py, findStars.py, Centroid.py and moveto.py This takes
you through the guiding loop.  Based in part on the doPyGuide.py test routine
included with PyGuide."""

import os
os.environ["NUMERIX"] = "numarray" # make pyfits use numarray
import sys
#import numarray as num
import pyfits
import pywcs
import PyGuide
#import RO.DS9
import pylab as py
import matplotlib.patches as pch
import numpy as np
import time
import math
import Image, ImageDraw
import threading 
import subprocess
import wx

# Set the system path to the root directory of the Nessi set of libraries so we 
# can import our library modules in a consistent manner.
#sys.path[0] = os.path.split(os.path.abspath(sys.path[0]))[0]
import nessi_settings as settings
from indiclient import *

#for comminicating between panels
from wx.lib.pubsub import Publisher as pub

# Default Parameters
# these settings will need to be updated once we have the real guide camera
# in order, bias (ADU), readnoise (e-), gain (e-/ADU), saturation level (ADU)
ccdInfo = PyGuide.CCDInfo(100.0, 12.5, 1.5, 65535)
# these are general settings
thresh = 5.0
radMult = 3.0
rad = 15
satLevel = (2**16)-1
verbosity = 2
doDS9 = False
mask = None
satMask = None

DEBUG = False
# Wrap functions based on those from the RO.MathUtil module by Russel Owens

def wrapAlt(angDeg):
    """Returns the floating point angle (in degrees) wrapped into the range (0, 85] to ensure 
    telescope is not sent to an impossible Alt, should be low probability usage, 
    but better to be safe.  Range is 85 deg. to stay away from zenith."""
    # If alt is less than 85 deg. ok to go
    if angDeg <= 90.0:
        return angDeg
    # Don't allow below horizon
    elif angDeg < 0.0:
        return 0.0
    # if alt is greather than 90, need to modify.
    elif angDeg > 85.0:
       return 85.0
        
def wrapCtr(angDeg):
    """Returns the floating point angle (in degrees) wrapped into the range (-180, 180]"""
    # First wrap into [0, 360]; result is 360 if ctrAng < 0 but so near 0 that adding 360 rounds it
    ctrAng = math.fmod(angDeg, 360.0)
    if ctrAng > 180.0:
        ctrAng -= 360.0
    return ctrAng

def wrapPos(angDeg):
    """Returns the floating point angle (in degrees) wrapped into the range [0, 360)"""
    res = math.fmod(angDeg, 360.0)
    # First wrap into [0, 360]; result is 360 if ctrAng < 0 but so near 0 that adding 360 rounds it
    if res == 360.0:
        return 0.0
    elif res < 0.0:
        res = 360.0 + res
    return res

def xy_move(centroidMaster, centroidMinion):
    """Finding the distance to move and if the move should happen."""
    #what is the shift? Think of the output as how much to shift the frame by, not move the point.
    deltaxy = [centroidMinion[0] - centroidMaster[0], centroidMinion[1] - centroidMaster[1]]
    #set threshold for telescope movement - makes assumption of 0.23"/px plate scale and minimum movement of 0.05" (0.05/0.23 = 0.21)
    if math.sqrt(deltaxy[0]**2 + deltaxy[1]**2) <= 0.21:
        move = False
        return deltaxy, move
    else:
        move = True
        return deltaxy, move

#"""Functions that run in the main loop"""            
##get the master frame for choosing guide star            
#def get_master():
#    masterframe = pic.getfits("test2.fits")
#    return masterframe

##need to change stars?
#def changestar(newstar, currentdata):
#    if newstar == True:
#        print currentdata, mask, satMask, ccdInfo, thresh, radMult, rad, verbosity, doDS9
#        starlist = PyGuide.findStars(currentdata, mask, satMask, ccdInfo, thresh,
#                                        radMult, rad, verbosity, doDS9)
#        return starlist
#    else: 
#        return

#def choosestar(currentdata):
#    py.clf()
#    fig = py.figure(1)
#    a = fig.gca()
#    py.imshow(np.log10(currentdata), cmap=py.cm.Greys)
#    for l in range(15):
#        labels = py.text(stars[0][l].xyCtr[0]+10, stars[0][l].xyCtr[1]+15, l, backgroundcolor='m', color='white')
#        starcirc = pch.Circle(stars[0][l].xyCtr, radius=5, color='m', fill=False)
#        a.add_patch(starcirc)
#    py.savefig('choose.png')

#def newfield():
#    print 'acquiring new field'
#    global masterfield
#    masterfield = get_master()

#def findstars():
#    print 'finding stars'
#    global stars
#    stars = changestar(True, masterfield)

#def selectstar():
#    print 'selecting star'
#    choosestar(masterfield)
#    im = Image.open("choose.png")
#    im.show()
    
#def star():
#    inputstar = raw_input("Star # >> ")
#    global starinfo
#    starinfo = stars[0][int(inputstar)]
#    print starinfo
#    print starinfo.xyCtr
                
#def closeloop():
#    print 'closing the loop'
#    logfile = time.strftime("%a%d%b%Y-%H:%M:%S.log", time.gmtime())
#    global log
#    log = open(logfile, 'a')
#    global master
#    master = PyGuide.Centroid.centroid(masterfield, mask, satMask, starinfo.xyCtr, 3, ccdInfo)
#    log.write('Initial Centroid            Initial Error\n' + 'X             Y             Xerr           Yerr\n' + str(master.xyCtr[0]) + ' ' +  str(master.xyCtr[1]) + ' ' +  str(master.xyErr[0]) + ' ' +  str(master.xyErr[1]) + '\n\n' + 'Guiding corrections:\n' + 'Centroid                    Error\n' + 'X             Y             Xerr          Yerr          Time(UTC)\n')
#    guideloop = LoopThread()
#    guideloop.start()
#    #commend out next two lines to speed test
#    raw_input("Hit <enter> to stop guiding \n")
#    guideloop.running = False
#    guideloop.join()


#def find_centroid(image, xyguess):
#    pass
class SeriesExpThread(threading.Thread):
    """Thread to run the guiding loop"""
    def __init__(self, window, event, scount, scadence):
        """Initialize the guiding thread"""
        super(SeriesExpThread, self).__init__()

        # Attributes
        self.window = window
        self.event = event
        self.scount = scount
        self.scadence = scadence
               
    def run(self):
        i = 0
        while i < self.scount:
            """take an exposure with current settings"""
            if self.window.seriesstatus.isSet():
                self.window.SeriesUpdate(i, self.scount)
                self.window.Expose(self.event)
                time.sleep(float(self.scadence))    
                i += 1
            else:
                break
        self.window.SeriesCancel('Finished')

def timeout_handler(devicename,vectorname,indi):
    if DEBUG: print "Timeout",devicename,vectorname
    raise Exception

def move_scope(newra, newdec):
#    #get current ra, dec
#    ra = dec = 0.00
#    try: 
#        indi=indiclient(settings.scope,7624)
#        #time.sleep(1)
#        indi.set_timeout_handler(timeout_handler)
#        try:
#            teldata = indi.get_vector("Telescope","Pointing") 
#            #ra
#            ra = teldata.get_element("RA2k").get_float()
#            #dec
#            dec = teldata.get_element("Dec2k").get_float()
#            if DEBUG: print 'current ra dec: ', ra, dec 
#        except:
#            pass
#    except:
#        pass
    # convert RA in decimal degrees back to RA in decimal hours
    newra = newra/15.0
    try:
        new = str(newra) + ';' + str(newdec)
        if DEBUG: print 'setINDI -h ' + settings.scope + ' \"Telescope.SetRaDec2k.RA2k;Dec2k=' + new + '\"'
        subprocess.Popen('setINDI -h ' + settings.scope + ' \"Telescope.SetRaDec2k.RA2k;Dec2k=' + new + '\"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        #refresh with new data
        indi=indiclient(settings.scope,7624)
        indi.set_timeout_handler(timeout_handler)
        teldata = indi.get_vector("Telescope","Pointing") 
        #ra
        ra = teldata.get_element("RA2k").get_float()
        #dec
        dec = teldata.get_element("Dec2k").get_float()
        if DEBUG: print 'current ra, dec: ', ra, dec 
    except:
        pass
    
    indi.quit()

class GuideThread(threading.Thread):
    """Thread to run the guiding loop"""
    def __init__(self, window, initialxy, cadence):
        """Initialize the guiding thread"""
        super(GuideThread, self).__init__()

        # Attributes
        self.window = window
        self.cadence = cadence
        self.initialxy = initialxy
        self.firsttime = True
        #open guiding log
        if self.window.guide_log_status:
            self.open_guidelog()
            self.window.autosave_cb.SetValue(True)
       
    def run(self):
        """Actual guiding loop"""
        while self.window.guidestatus.isSet():
            #get the new image 
            if DEBUG: print "get image..."
            self.window.Expose(None)
            if self.firsttime:
                master_image = self.window.fits
                #get data from fits image
                master_data = master_image[0].data
            else:
                minion_image = self.window.fits
                #get data from fits image
                minion_data = minion_image[0].data
            #find the new centroid
            if DEBUG: print "get centroid..."
            if self.firsttime:
                #set to both master and minion centroid vars as that way the next
                #time through the centroid has an initial guess
                self.master_centroid = self.minion_centroid = PyGuide.Centroid.centroid(master_data, mask, satMask, self.initialxy, rad, ccdInfo)
                if not self.master_centroid.isOK:
                    self.window.GuideError('Can\'t find star!')
                
                if DEBUG: print "master centroid:", self.master_centroid
            else:
                self.minion_centroid = PyGuide.Centroid.centroid(minion_data, mask, satMask, self.minion_centroid.xyCtr, rad, ccdInfo)
                if DEBUG: print "minion centroid:", self.minion_centroid
                if not self.minion_centroid.isOK:
                    self.window.GuideError('Lost guide star!')
                
            #calculate the xy shift
            if DEBUG: print "get xy shift..."
            if self.firsttime:
                if DEBUG: print "skip get xy"
            else:
                shift = xy_move(self.master_centroid.xyCtr, self.minion_centroid.xyCtr)
                self.window.Update(shift, self.minion_centroid.xyCtr)
                if DEBUG: print shift
            #convert to telescope RA, Dec shift
            if DEBUG: print "convert to telescope coords..."
            if self.firsttime:
                if DEBUG: print "skip convert to t coords"
                
            else:
                if DEBUG: print "tele coords"
                # New RA and Dec Coordinates to move to
                wcs = pywcs.WCS(minion_image[0].header)
                pixcrd = np.array([[512.0+shift[0][0],512.0+shift[0][1]]], np.float_)
                # Convert pixel coordinates to world coordinates
                # The second argument is "origin" -- in this case we're declaring we
                # have 1-based (Fortran-like) coordinates.
                sky = wcs.wcs_pix2sky(pixcrd, 1)

            if DEBUG: print "move telescope..."
            if self.firsttime:
                if DEBUG: print "skip moving"
                
            else:
                print "moving scope"
                move_scope(sky[0][0], sky[0][1])
#                pub.sendMessage("LOG EVENT", str(altaz_shift[0]) )
            #update guide info/plot panels and send to log
            if DEBUG: print "update log and info/plot panels..."
            if self.window.guide_log_status:
                if self.firsttime:
                    if DEBUG: print "update master position in log"
                    self.write_guidelog(self.master_centroid)
                    #write master fits file with updated header
                    
                else:
                    if DEBUG: print "minion position in log"
                    self.write_guidelog(self.minion_centroid)  
                    #write minion fits file with updated header
            else:
                pass
            
            #switch logic to do minion centroid and compare to master on all future
            #loops
            if self.firsttime:
                self.firsttime = False
                if DEBUG: print "self.firsttime=", self.firsttime
            
            #wait for given cadence before taking next guide image
            time.sleep(self.cadence)
            
            
    def open_guidelog(self):
        logtime = time.strftime("%a%d%b%Y-%H:%M:%S", time.gmtime())
        loggerfile = settings.save_folder+'guide'+logtime+".log"
        self.logfile = open(loggerfile, 'a')
        self.logfile.write('Starting up ' + logtime + '\n' +"First Line is Master Centroid" + '\n' + 'Centroid X    ' + 'Centroid Y    ' + 'X error       ' + 'Y error       ' + 'Time (GMT)')
    
    def write_guidelog(self, centroid):
        #write timestamp plus row of temps
        self.logfile.write('\n' + str(centroid.xyCtr[0]).ljust(13,'0') + ' ' + str(centroid.xyCtr[1]).ljust(13,'0') + ' ' + str(centroid.xyErr[0]).ljust(13,'0') + ' ' + str(centroid.xyErr[1]).ljust(13,'0') + ' ' + time.strftime("%a%d%b%Y %H:%M:%S", time.gmtime()))        
                
            
    def check_mask():
        #pixscale = moveto.get_wcs
        aperture_centroid = (36.0,48.0)
        aperture_hwidth = 5