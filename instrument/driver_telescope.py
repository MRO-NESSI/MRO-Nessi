#!/usr/bin/env python
"""API to talk to the MRO 2.4m telescope. Some code from Bill Ryan's acquire.py is used."""

import math
import os, time, sys
import datetime 

# Set the system path to the root directory of the Nessi set of libraries so we 
# can import our library modules in a consistent manner.
#sys.path[0] = os.path.split(os.path.abspath(sys.path[0]))[0]

import jdcal
#import gui.amasing_settings as settings
from indiclient import *

DEBUG = False

def RAFloatToString(ra):
#
# convert ra to hms string
    hours = int(math.floor(ra))
   
    decimalmins = round(((ra)- float(hours))*60.0,5)
    minutes = int(math.floor(decimalmins))

    seconds = round((decimalmins - float(minutes))*60.0,2)
    wholesecs = int(math.floor(seconds))
    hundrethsecs = int(100*(seconds-float(wholesecs)))

    minstr = str(minutes).zfill(2)
    secstr = str(wholesecs).zfill(2)
    fsecstr= str(hundrethsecs).zfill(2)

    if DEBUG: print " %d:%d:%5.2f" % (hours, minutes, seconds)
    rastring = str(hours)+":"+minstr+":"+secstr+"."+fsecstr
    return rastring

def DecFloatToString(dec):
#
# convert dec to dms string
    sign = int(dec/abs(dec))
    degrees = int(math.floor(abs(dec)))
   
    decimalmins = round(((abs(dec))- float(degrees))*60.0,5)
    minutes = int(math.floor(decimalmins))

    seconds = round((decimalmins - float(minutes))*60.0,2)
    wholesecs = int(math.floor(seconds))
    hundrethsecs = int(100*(seconds-float(wholesecs)))

    minstr = str(minutes).zfill(2)
    secstr = str(wholesecs).zfill(2)
    fsecstr= str(hundrethsecs).zfill(2)
    if DEBUG: print " %d:%d:%5.2f" % (hours, minutes, seconds)
    decstring = str(degrees)+":"+minstr+":"+secstr+"."+fsecstr
    if sign < 0: decstring="-"+decstring 
    return decstring

def jul_greg(jd):
    d = jdcal.jd2gcal(0, jd)
    g = datetime.timedelta(days=d[3])
    hrs = g.seconds / 3600
    min = (g.seconds % 3600) / 60
    sec = g.seconds % 60
    decsec = 0 # uncomment if need greater precision: g.microseconds/1E6
    
    date = str(d[0]).zfill(4) + str(d[1]).zfill(2) + str(d[2]).zfill(2) + str(hrs).zfill(2) + str(min).zfill(2) + str(sec + decsec)
    return date

class ScopeData(threading.Thread):
    def __init__(self, window, inditelhost, keywords):
        """Init Worker Thread Class."""
        super(ScopeData, self).__init__()
        
        # Attributes
        
        self.window = window
        self.inditelhost = inditelhost
        self.keywords = keywords
        
# define alternate timeout handler to avoid infinite error loop
    def timeout_handler(devicename,vectorname,indi):
        if DEBUG: print "Timeout",devicename,vectorname
        raise Exception
                
    def run(self):
#def GetIndiTelData(inditelhost, keywords): 
## MRO specific at this point; port hardwired to 7624


 
#NOTE: dcd get text has errors? use float and convert instead.
        try: 
            indi=indiclient(self.inditelhost,7624)
            #time.sleep(1)
            indi.set_timeout_handler(self.timeout_handler)
            try:
                teldata = indi.get_vector("Telescope","Pointing") 
                #ra
                ra = teldata.get_element("RA2K").get_float()
                self.keywords["CRVAL1"] = 15.0*ra
                self.keywords["ra"] = RAFloatToString(ra) 
                #dec
                dec = teldata.get_element("Dec2K").get_float()
                self.keywords["CRVAL2"] = dec
                self.keywords["dec"] = DecFloatToString(dec) 
                #airmass
                am = teldata.get_element("AM").get_float()
                self.keywords["airmass"] =  round(am,5)
                #alt
                alt = teldata.get_element("Alt").get_float()
                self.keywords["telalt"] =  round(alt,5)
                #az
                az = teldata.get_element("Az").get_float()
                self.keywords["telaz"] =  round(az,5)
                #focus
                focus = teldata.get_element("Focus").get_float()
                self.keywords["focus"] =  round(focus,6)
                #parallactic angle
                pa = teldata.get_element("PA").get_float()
                self.keywords["pa"] =  round(pa,6)
                jd = teldata.get_element("JD").get_float()
                gdate = jul_greg(jd)
                self.keywords["jd"] = jd
                self.keywords["gdate"] = gdate
            except:
                if DEBUG: print "WARNING. No TCS info found."

            #check if environmental data available
            try:
            # wind speed
                envdata = indi.get_vector("Environment","Now")
                windvel = envdata.get_element("WindSpeed").get_text()
                self.keywords["windvel"] =  str(windvel)
            # wind gust
                windgust = envdata.get_element("WindGust").get_text()
                self.keywords["windgust"] = str(windgust)
            # wind direction
                winddir = envdata.get_element("WindDir").get_text()
                self.keywords["winddir"] = str(winddir)

            except:
                if DEBUG: print "WARNING. No environmental data found."

            indi.quit()
        except:
            if DEBUG: print "WARNING. No connection to telescope found."
###following line is to take the place of rotator
        self.keywords["CROTA2"] = -pa -alt
        
        self.window.set_keywords(self.keywords)
        self.window.done = True        # to do - add error checking