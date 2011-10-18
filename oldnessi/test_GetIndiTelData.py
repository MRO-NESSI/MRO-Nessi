#!/usr/bin/env python

#test_GetIndiTelData.py        Bill Ryan       1 Aug 2008 

# Toy program to test function that grabs telescope pointing data 
# and returns it in a python dictionary (associative array).
# 
# Requires indiclient.py from http://pygtkindiclient.sourceforge.net/  

import sys                # standard lib, python should be able to find it
sys.path.append("./lib")  # point to location to find indiclient.py
from indiclient import *

#-------------------------------------------------------
def GetIndiTelData(inditelhost, keywords): 
# MRO specific at this point; port hardwired to 7624
 
#NOTE: dcd get text has errors? use float and convert instead.
   try: 
      indi=indiclient(inditelhost,7624)      
      #ra
      ra = indi.get_text("Telescope","Pointing","RA2K")
      keywords["ra"] = ra 
      #dec
      dec = indi.get_text("Telescope","Pointing","Dec2K")
      keywords["dec"] = dec 
      #airmass
      am = indi.get_float("Telescope","Pointing","AM")
      keywords["airmass"] =  str(round(am,5))
      #alt
      alt = indi.get_float("Telescope","Pointing","Alt")
      keywords["telalt"] =  str(round(alt,5))
      #az
      az = indi.get_float("Telescope","Pointing","Az")
      keywords["telaz"] =  str(round(az,5))
      #focus
      focus = indi.get_float("Telescope","Pointing","Focus")
      keywords["focus"] =  str(round(focus,6))
      indi.quit()
   except:
      print "WARNING. No TCS info found."

   return 0   # to do - add error checking
#------------------------------------------------------------

#-main program--------------------------------

# try it

inditelhost = 'eos.nmt.edu'
keywords={}

GetIndiTelData(inditelhost,keywords)

print keywords

# print in prettier format
for key in keywords.keys():
   print "%10s  ->  %10s" % (key, keywords[key])
