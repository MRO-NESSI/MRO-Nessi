#!/usr/bin/env python
"""Guider connects getim.py, findStars.py, Centroid.py and moveto.py This takes
you through the guiding loop.  Based in part on the doPyGuide.py test routine
included with PyGuide."""
import pywcs
import PyGuide
import numpy as np
from time import sleep
import math
from threading import Thread
import subprocess

# Preferences 
#TODO: WE NEED THESE
#config = prefcontrol.getConfig()
#scope = config['scope server']
#scopeport = config['scope port']
#savefolder = config['savefolder']
        
from nessi.indiclient import *

# Default Parameters
# TODO: Update these to the camera
ccdInfo = PyGuide.CCDInfo(100.0, 12.5, 1.5, 65535)
thresh = 5.0
radMult = 3.0
rad = 15
satLevel = (2**16)-1
verbosity = 2
mask = None
satMask = None

class GuideThread(Thread):
    """Thread to run the guiding loop"""
    def __init__(self, window, initialxy, cadence):
        """Initialize the guiding thread"""
        super(GuideThread, self).__init__()

        # Attributes
        self.window = window
        self.cadence = cadence
        self.initialxy = initialxy

        self.master_image    = None
        self.master_data     = None
        self.master_centroid = None

        self.minion_image    = None
        self.minion_data     = None
        self.minion_centroid = None

        #TODO: implement
        self.master_image    = takePictureFits()
        self.master_data     = self.master_image[0].data
        try:
            self.master_centroid = PyGuide.Centroid.centroid(
                self.master_data, mask, satMask, self.initialxy, rad, ccdInfo)
        except:
            #TODO: catch correctly
            pass

    def run(self):
        #TODO: Make event
        while True:
            #TAKE NEW PICTURE
            self.minion_image    = takePictureFits()
            self.minion_data     = self.minion_data[0].data
            try:
                self.minion_centroid = PyGuide.Centroid.centroid(
                    self.minion_image,
                    mask, satMask,
                    self.initialxy,
                    rad, ccdInfo)
            except:
                #TODO: catch correctly
                pass

            #CALC XY SHIFT
            sky_shift = self.calc_shift()

            #MOVE
            move_scope(sky_shift[0][0], sky_shift[0][1])
                       
            #WAIT
            sleep(self.cadence)

    def calc_shift(self):
        shift_xy = xy_move(self.master_centroid.xyCtr, 
                           self.minion_centroid.xyCtr)
        wcs = pywcs.WCS(minion_image[0].header)
        pixcrd = np.array([[512.0+shift_xy[0][0],512.0+shift_xy[0][1]]],
                          np.float_)
        sky_cord = wcs.wcs_pix2sky(pixcrd, 1)
        return sky_cord


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

def move_scope(newra, newdec):
    # convert RA in decimal degrees back to RA in decimal hours
    newra = newra/15.0
    try:
        new = str(newra) + ';' + str(newdec)
        subprocess.Popen('setINDI -h ' + scope + ' \"Telescope.SetRaDec2k.RA2k;Dec2k=' + new + '\"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        #refresh with new data
        indi=indiclient(scope,7624)
        indi.set_timeout_handler(timeout_handler)
        teldata = indi.get_vector("Telescope","Pointing") 
        #ra
        ra = teldata.get_element("RA2k").get_float()
        #dec
        dec = teldata.get_element("Dec2k").get_float()
    except:
        pass
    finally:
        indi.quit()

def timeout_handler(devicename,vectorname,indi):
    raise Exception
