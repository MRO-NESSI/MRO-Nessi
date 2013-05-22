#!/usr/bin/env python
"""
 Control software for NESSI
 
 author:       Luke Schmidt, Matt Napolitano
 author_email: lschmidt@nmt.edu
"""

__author__ = 'Luke Schmidt, Matt Napolitano'
__date__ = '2013'

#Live update plotting of temps with matplot lib from code by Eli Bendersky
#http://eli.thegreenplace.net/2008/08/01/matplotlib-with-wxpython-guis/

# General Modules
import os, sys
import random
import time
import pprint
import cStringIO
import wx
import usb.core
import usb.util
import numpy as np
import math
from datetime import datetime

# Threading and Multiprocess
import threading
import subprocess
import threadtools #module from wxPython Cookbook by Cody Precord

# Images
import ds9

# Preferences for GUI
import prefcontrol

# Communicating between panels
from wx.lib.pubsub import Publisher as pub

# Plotting
import matplotlib
matplotlib.interactive( True )
matplotlib.use( 'WXAgg' )

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas, NavigationToolbar2WxAgg as NavigationToolbar
import pylab

# Drivers and Custom Modules
import FLI
from guider import GuideThread, SeriesExpThread
from driver_telescope import ScopeData

#from wx.lib.stattext import GenStaticText
#image manipulation
#import Image
#import backend.pic as pic

# Set the system path to the root directory of the Nessi set of libraries so we 
# can import our library modules in a consistent manner.
#sys.path[0] = os.path.split(os.path.abspath(sys.path[0]))[0]
#import all of the control libraries

random.seed()

DEBUG = False

################# Master Dictionary for Instrument State #######################

keywords = {"OBSERVER"  : "Observer",
            "INST"      : "NESSI",
            "TELESCOP"  : "MRO 2.4m",
            "FILENAME"  : "default",
            "IMGTYPE"   : "imgtyp",
            "RA"        : "TCS down" ,   
            "DEC"       : "TCS down",  
            "AIRMASS"   : "TCS down",       
            "TELALT"    : "TCS down",
            "TELAZ"     : "TCS down",
            "TELFOCUS"  : "TCS down",
            "PA"        : "TCS down",
            "JD"        : "TCS down",
            "GDATE"     : "TCS down",
            "WINDVEL"   : "No Env data",
            "WINDGUST"  : "No Env data",
            "WINDDIR"   : "No Env data",
            "REI12"     : 0.0, # focus position
            "REI34"     : 0.0, # focus position
            "MASK"      : "None",
            "FILTER1"   : "None",
            "FILTER2"   : "None",
            "GRISM"     : "None",
            "EXP"       : 0.0,
            "CAMTEMP"   : 0.0,
            "CTYPE1"    : "RA---TAN",
            "CTYPE2"    : "DEC--TAN",
            "CRPIX1"    : 512.0,
            "CRPIX2"    : 512.0,
            "CDELT1"    : 0.0, 
            "CDELT2"    : 0.0,
            "CRVAL1"    : 0.0, 
            "CRVAL2"    : 0.0,
            "CROTA2"    : 0.0
            }
                        
class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="NESSI Controller", size=(850,875))

        # Here we create a panel and a notebook on the panel
        self.create_menus()
        self.CreateStatusBar()
        
        p = wx.Panel(self)
        nb = wx.Notebook(p, style=wx.NB_RIGHT)

        # create the page windows as children of the notebook
        page1 = PageOne(nb)
        page2 = PageTwo(nb)
        page3 = PageThree(nb)
        page4 = PageFour(nb)
        page5 = PageFive(nb)

        # add the pages to the notebook with the label to show on the tab
        nb.AddPage(page1, "Overview")
        nb.AddPage(page2, "K-Mirror")
        nb.AddPage(page3, "Guiding")
        nb.AddPage(page4, "Settings")
        nb.AddPage(page5, "Log")

        # Add icon
        path = "media/nessi.png"
        icon = wx.Icon(path, wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)
        
        pub.subscribe(self.change_statusbar, 'change_statusbar')
        
        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)
        
    def change_statusbar(self, msg):
        self.SetStatusText(msg.data)
        
    def create_menus(self):
        menuBar = wx.MenuBar()

        # Attributes
        FileMenu = wx.Menu()
        about_item   = FileMenu.Append(wx.ID_ABOUT, text="&About NESSI Controller")
        quit_item    = FileMenu.Append(wx.ID_EXIT, text="&Quit")
        
        # Event Handlers
        self.Bind(wx.EVT_MENU, self.OnAbout, about_item)
        self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
        
        menuBar.Append(FileMenu, "&File")
        self.SetMenuBar(menuBar)

    def OnQuit(self, event=None):
        self.Close()
        
    def OnAbout(self, event=None):
        info = wx.AboutDialogInfo()
        info.SetName('NESSI Controller')
        info.SetVersion('0.1')
        info.SetDescription('NESSI Controller is an interface to the New Mexico Tech Extrasolar Spectroscopic Survey Instrument. Email lschmidt@nmt.edu with questions.')
        info.SetCopyright('(C) 2013 Luke Schmidt, Matt Napolitano, NMT/MRO')

        wx.AboutBox(info)


if __name__ == "__main__":
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()
