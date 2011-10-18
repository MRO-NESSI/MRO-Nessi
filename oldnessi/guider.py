#!/usr/bin/env python
"""Guider connects getim.py, findStars.py, Centroid.py and moveto.py This takes
you through the guiding loop.  Based in part on the doPyGuide.py test routine
included with PyGuide."""

import os
os.environ["NUMERIX"] = "numarray" # make pyfits use numarray
import sys
import numarray as num
import pyfits
import PyGuide
import RO.DS9
import getim
import pixelmath
import pylab as py
import matplotlib.patches as pch
import numpy as np
import time
import Image, ImageDraw
from threading import Thread


# Default Parameters
# these settings will need to be updated once we have the real guide camera
ccdInfo = PyGuide.CCDInfo(100.0, 12.5, 1.5, 65535)
# these are general settings
thresh = 5.0
radMult = 3.0
rad = 15
satLevel = 255#(2**16)-1
verbosity = 0
doDS9 = False
mask = None
satMask = None

"""Functions that run in the main loop"""            
#get the master frame for choosing guide star            
def get_master():
    masterframe = getim.getimg("test2.fits")
    return masterframe

#need to change stars?
def changestar(newstar, currentdata):
    if newstar == True:
        starlist = PyGuide.findStars(currentdata, mask, satMask, ccdInfo, thresh,
                                        radMult, rad, verbosity, doDS9)
        return starlist
    else: 
        return

def choosestar(currentdata):
    py.clf()
    fig = py.figure(1)
    a = fig.gca()
    py.imshow(np.log10(currentdata), cmap=py.cm.Greys)
    for l in range(15):
        labels = py.text(stars[0][l].xyCtr[0]+10, stars[0][l].xyCtr[1]+15, l, backgroundcolor='m', color='white')
        starcirc = pch.Circle(stars[0][l].xyCtr, radius=5, color='m', fill=False)
        a.add_patch(starcirc)
    py.savefig('choose.png')

def newfield():
    print 'acquiring new field'
    global masterfield
    masterfield = get_master()

def findstars():
    print 'finding stars'
    global stars
    stars = changestar(True, masterfield)

def selectstar():
    print 'selecting star'
    choosestar(masterfield)
    im = Image.open("choose.png")
    im.show()
    
def star():
    inputstar = raw_input("Star # >> ")
    global starinfo
    starinfo = stars[0][int(inputstar)]
    print starinfo
    print starinfo.xyCtr
                
def closeloop():
    print 'closing the loop'
    logfile = time.strftime("%a%d%b%Y-%H:%M:%S.log", time.gmtime())
    global log
    log = open(logfile, 'a')
    global master
    master = PyGuide.Centroid.centroid(masterfield, mask, satMask, starinfo.xyCtr, 3, ccdInfo)
    log.write('Initial Centroid            Initial Error\n' + 'X             Y             Xerr           Yerr\n' + str(master.xyCtr[0]) + ' ' +  str(master.xyCtr[1]) + ' ' +  str(master.xyErr[0]) + ' ' +  str(master.xyErr[1]) + '\n\n' + 'Guiding corrections:\n' + 'Centroid                    Error\n' + 'X             Y             Xerr          Yerr          Time(UTC)\n')
    guideloop = LoopThread()
    guideloop.start()
    #commend out next two lines to speed test
    raw_input("Hit <enter> to stop guiding \n")
    guideloop.running = False
    guideloop.join()
    
class GuideThread(Thread):
    """Main thread to handle guiding input commands"""
    def __init__(self):
        Thread.__init__(self)
        self.running = True
        
    def run(self):
        while self.running:
            #get keyboard input for now, later this will be button input
            input = raw_input(">> ")
            if input == 'exit':
                self.running = False
            elif input =='newfield':
                newfield()
            elif input =='findstars':
                findstars()
            elif input =='selectstar':
                selectstar()
            elif input == 'star':
                star()
            elif input =='closeloop':
                closeloop()
            else:
                print 'unrecognized command'
                
    
    
class LoopThread(Thread):
    """Thread to run the guiding loop"""
    def __init__(self):
        """Initialize the guiding thread"""
        Thread.__init__(self)
        self.running = True
        
    def run(self):
        """Actual guiding loop"""
        while self.running:
            i=1
            minionfield = getim.fakeit(i)
            minion = PyGuide.Centroid.centroid(minionfield, mask, satMask, starinfo.xyCtr, rad, ccdInfo)
            shift = pixelmath.move_scope(master.xyCtr, minion.xyCtr)
            log.write(str(minion.xyCtr[0]) + ' ' + str(minion.xyCtr[1]) + ' ' +  str(minion.xyErr[0]) + ' ' +  str(minion.xyErr[1]) + ' ' + time.strftime("%H:%M:%S", time.gmtime()) + '\n')
            print shift
            #next line for speed testing purposes, i.e. run once
            #self.running = False
            
            
    def check_mask():
        #pixscale = moveto.get_wcs
        aperture_centroid = (36.0,48.0)
        aperture_hwidth = 5


if __name__== '__main__':
    #create main thread
    mainthread = GuideThread()
    #start it up
    mainthread.start()
