#!/usr/bin/env python
"""This module holds all of the math required by the tracking algorithm.  In
addition there are some functions to get telescope telemetry data, find north and
hopefully at some point automatically do astrometry on the image."""

import subprocess
import pyfits
import ephem
import math

"""get WCS data via astrometry.net see docs for how to run solve-field need to
make sure that scale etc. is set otherwise the solve will take quite a long time"""

#runs astrometry.net to solve plate scale, orientation etc.
def locate(rawfits):
    subprocess.call('/usr/local/astrometry/bin/solve-field --cpulimit 20 --scale-units arcsecperpix --scale-low 2.25 --scale-high 2.35 --depth 20,30,40 --overwrite %s' % rawfits, shell=True) 

#gets the updated wcs data after running get_wcs via wcsinfo program from astrometry.net
def get_wcs(processed):
    wcs = subprocess.Popen('/usr/local/astrometry/bin/wcsinfo %s' % processed, shell=True, stdout=subprocess.PIPE)
    wcsinfo = wcs.communicate()[0]
    #format output into useable dictionary
    wcsout = wcsinfo.split('\n')
    wcsformated = dict([wcsout[i].split(' ') for i in range(len(wcsout)-1)])
    return wcsformated

#get telemetry data from the telescope, including, alt, az, pa, time, etc.
def telemetry(scope):
    global alt, az, pa, ha, lat  

#Calculate distance to move in xy coords
def move_scope(centroidMaster, centroidMinion):
    #what is the shift? Think of the output as how much to shift the frame by, not move the point.
    deltaxy = [centroidMinion[0] - centroidMaster[0], centroidMinion[1] - centroidMaster[1]]
    #set threshold for telescope movement - makes assumption of 0.23"/px plate scale and minimum movement of 0.05" (0.05/0.23 = 0.21)
    if math.sqrt(deltaxy[0]**2 + deltaxy[1]**2) <= 0.21:
        move = False
        return deltaxy, move
    else:
        move = True
        return deltaxy, move

#calculate the instantaneous rotation rate of the k-mirror - run as often as
#necessary for a given pixel scale.
def rot_rate():
    #get alt, az, pa from telescope
    
    """The following is based on discussions in "The Design and Construction of Large
    Optical Telescopes" edited by Bely along with "MMTO Internal Technical Memorandum
    #04-1" by G. Schmidt.
    
    alt = altitude, az = azimuth, pa = parallactic angle, ha = hour angle, lat = latitude
    
    using eq. 6.10 from Bely and the conversion from d(pa)/d(ha) to d(pa)/d(t):
    d(ha)/d(t) =  15deg/hr = 0.262 rad/hr
    
    The 0.5 is because the k-mirror rotates the image twice as fast as the physical
    rotation rate."""
    #calculate the current rotation rate
    dPAdT = -0.262*0.5*cos(radians(lat))*cos(radians(az))/cos(radians(alt))
    
    return dPAdT

"""We need to define a home position for k-mirror to figure north position as
well as how much we need to rotate to reach proper mask orientation"""
def north(port):
    #this will give the current vector for North in the image
    if port == 'cassegrain':
        north_ang = pa
    elif port == 'lnasmyth':
        north_ang = pa + alt
    elif port == 'rnasmyth':
        north_ang = pa - alt
    return north_ang
