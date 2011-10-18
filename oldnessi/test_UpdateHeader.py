#!/usr/bin/env python

#test_UpdateHeader.py        Bill Ryan       1 Aug 2008 

# Toy program to test function to update fits header from info
# stored in a python dictionary (associative array).

# Requires pyfits http://www.stsci.edu:8083/resources/software_hardware/pyfits
 
import sys                # standard lib, python should be able to find it.
sys.path.append("./lib")  # point to location to find pyfits.py
import pyfits

#-----------------------------------------------------------------
def UpdateHeader(fitsfile, headerkey):
#
# update header with values stored in dictionary headerkey.
# requires pyfits

   returnValue = 0

# open file and access header
   f = pyfits.open(fitsfile,mode='update')
   hdr = f[0].header

# start updating
   hdr.update('imagetyp',headerkey["imagetype"],'image type (object, flat,dark, etc)')
   hdr.update('object',  headerkey["object"],   'Target object')
   hdr.update('ra',      headerkey["ra"],       'RA at Equinox')
   hdr.update('dec',     headerkey["dec"],      'Dec at Equinox')
   hdr.update('airmass', headerkey["airmass"],  'Airmass at beginning of exposure')

# save file
   f.flush()

#TODO - add real return values

   return returnValue

#--------------------------------------------------
def GetIndiTelData(inditelhost, keywords):  
   rastr,decstr = "14:00:04.21","-07:21:38.9"  # make up and return some 
   keywords["ra"] = rastr                      # some fake data
   keywords["dec"] = decstr 
   keywords["airmass"] = "1.32" 

#---------------------------------------------------

#-main program--------------------------------

# try it

fitsfile="a0001.fits"

keywords= {"imagetype":  "flat",          # some initial values
            "object":    "flatR",
            "ra":        "tcs down" ,
            "dec":       "tcs down",
            "airmass" :  "tcs down" }

inditelhost = "some_telescope"     # fake INDI or other telescope call
if inditelhost:
   GetIndiTelData(inditelhost, keywords)

UpdateHeader (fitsfile, keywords)

