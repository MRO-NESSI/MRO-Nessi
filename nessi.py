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


class FilterPanelOne(wx.Panel):
    """This panel controls the FLI filter wheel """
    def __init__(self, parent, *args, **kwargs):
        super(FilterPanelOne, self).__init__(parent) 
        
        self.parent = parent

        # Attributes
        self.filters = ['J', 'H', 'K', 'Open']
    
        self.curr_filter_text = wx.StaticText(self, label="Current Filter:")
        self.curr_filter = wx.StaticText(self, label="Checking...")
        self.select_button = wx.Button(self, label="Select")
        self.filter_choice = wx.ComboBox(self, -1, size=(100,-1), choices=self.filters, style=wx.CB_READONLY)
        
        # Layout
        self.__DoLayout()
        
        # Event Handlers
        self.filter_choice.Bind(wx.EVT_COMBOBOX, self.on_select)
        self.select_button.Bind(wx.EVT_BUTTON, self.move_filter)
        
        ## Layout for this panel:
        ##
        ##    0                      1
        ##   +-------------------+---------------------+
        ## 0 |  curr_filter_text |   curr_filter       |
        ##   +-------------------+---------------------+
        ## 1 |   select_button   |    filter_choice    |
        ##   +-------------------+---------------------+
    def __DoLayout(self):
        sbox = wx.StaticBox(self, label="Filter Wheel One")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.curr_filter_text,  pos=(0,0), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.curr_filter,  pos=(0,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.filter_choice, pos=(1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.select_button, pos=(1,1), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
    
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(200, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        
    def on_select(self, event):
        try:
            selected = event.GetSelection()
            status_update = "Chosen filter is..." + str(self.filters[selected])
            pub.sendMessage("LOG EVENT", status_update)
            return selected
        except ValueError:
            pass

    def move_filter(self, event):
        try:
            pub.sendMessage("LOG EVENT", "Moving to filter...")
            selected = self.filter_choice.GetSelection()
            self.curr_filter.SetLabel(self.filters[selected])
        except ValueError:
            pass
        
class FilterPanelTwo(wx.Panel):
    """This panel controls the FLI filter wheel """
    def __init__(self, parent, *args, **kwargs):
        super(FilterPanelTwo, self).__init__(parent) 
        
        self.parent = parent

        # Attributes
        self.filters = ['Open', 'Open', 'Open', 'Open']
    
        self.curr_filter_text = wx.StaticText(self, label="Current Filter:")
        self.curr_filter = wx.StaticText(self, label="Checking...")
        self.select_button = wx.Button(self, label="Select")
        self.filter_choice = wx.ComboBox(self, -1, size=(100,-1), choices=self.filters, style=wx.CB_READONLY)
        
        # Layout
        self.__DoLayout()
        
        # Event Handlers
        self.filter_choice.Bind(wx.EVT_COMBOBOX, self.on_select)
        self.select_button.Bind(wx.EVT_BUTTON, self.move_filter)
        
        ## Layout for this panel:
        ##
        ##    0                      1
        ##   +-------------------+---------------------+
        ## 0 |  curr_filter_text |   curr_filter       |
        ##   +-------------------+---------------------+
        ## 1 |   select_button   |    filter_choice    |
        ##   +-------------------+---------------------+
    def __DoLayout(self):
        sbox = wx.StaticBox(self, label="Filter Wheel Two")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.curr_filter_text,  pos=(0,0), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.curr_filter,  pos=(0,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.filter_choice, pos=(1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.select_button, pos=(1,1), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
    
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(200, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        
    def on_select(self, event):
        try:
            selected = event.GetSelection()
            status_update = "Chosen filter is..." + str(self.filters[selected])
            pub.sendMessage("LOG EVENT", status_update)
            return selected
        except ValueError:
            pass

    def move_filter(self, event):
        try:
            pub.sendMessage("LOG EVENT", "Moving to filter...")
            selected = self.filter_choice.GetSelection()
            self.curr_filter.SetLabel(self.filters[selected])
        except ValueError:
            pass

class FocusREI12(wx.Panel):
    """This panel controls the position of REI1-2 """
    def __init__(self, parent, *args, **kwargs):
        super(FocusREI12, self).__init__(parent) 
        
        self.parent = parent

        # Attributes    
        self.curr_pos_label = wx.StaticText(self, label="Position " + u'\u03bc' + "m:")
        self.curr_pos = wx.StaticText(self, label="...")
        
        self.goto_button = wx.Button(self, label="Set", size=(50,-1))
        self.goto_value = wx.TextCtrl(self, -1, '', size=(50,-1), style=wx.TE_NO_VSCROLL)
        
        self.in_button = wx.Button(self, label=u'\u21e6' + " In", size=(50,-1))
        self.step_size = wx.SpinCtrl(self, -1, '', (-1, -1),  (50, -1))
        self.step_size.SetRange(1, 1000)
        self.step_size.SetValue(0)
        self.out_button = wx.Button(self, label="Out " + u'\u21e8', size=(50,-1))
        
        # Layout
        self.__DoLayout()
        
        # Event Handlers
        
        ## Layout for this panel:
        ##
        ##    0                      1
        ##   +-------------------+---------------------+
        ## 0 |  curr_pos_label   |   curr_pos          |
        ##   +-------------------+---------------------+
        ## 1 |     in_button     |      out_button     |
        ##   +-------------------+---------------------+
    def __DoLayout(self):
        sbox = wx.StaticBox(self, label="Focus REI-1-2")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.curr_pos_label,  pos=(0,0), span=(1,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.curr_pos,  pos=(0,2), span=(1,2), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
        
        sizer.Add(self.goto_button, pos=(1,0), span=(1,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.goto_value, pos=(1,2), span=(1,2), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
    
        sizer.Add(self.in_button, pos=(2,0), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.step_size, pos=(2,1), span=(1,2), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.out_button, pos=(2,3), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(150, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        
class FocusREI34(wx.Panel):
    """This panel controls the position of REI1-2 """
    def __init__(self, parent, *args, **kwargs):
        super(FocusREI34, self).__init__(parent) 
        
        self.parent = parent

        # Attributes    
        self.curr_pos_label = wx.StaticText(self, label="Position " + u'\u03bc' + "m:")
        self.curr_pos = wx.StaticText(self, label="...")
        
        self.goto_button = wx.Button(self, label="Set", size=(50,-1))
        self.goto_value = wx.TextCtrl(self, -1, '', size=(50,-1), style=wx.TE_NO_VSCROLL)
        
        self.up_button = wx.Button(self, label=u'\u21e7' + " Up", size=(60,-1), style=wx.BU_LEFT)
        self.step_size = wx.SpinCtrl(self, -1, '', (-1, -1),  (50, -1))
        self.step_size.SetRange(1, 1000)
        self.step_size.SetValue(0)
        self.down_button = wx.Button(self, label= u'\u21e9' + "Down ", size=(60,-1), style=wx.BU_LEFT)
        
        # Layout
        self.__DoLayout()
        
        # Event Handlers
        
        ## Layout for this panel:
        ##
        ##    0                      1
        ##   +-------------------+---------------------+
        ## 0 |  curr_pos_label   |   curr_pos          |
        ##   +-------------------+---------------------+
        ## 1 |     in_button     |      out_button     |
        ##   +-------------------+---------------------+
    def __DoLayout(self):
        sbox = wx.StaticBox(self, label="Focus REI-3-4")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.curr_pos_label,  pos=(0,0), span=(1,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.curr_pos,  pos=(0,2), span=(1,2), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
        
        sizer.Add(self.goto_button, pos=(1,3), span=(1,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.goto_value, pos=(2,3), span=(1,1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
    
        sizer.Add(self.up_button, pos=(1,0), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.step_size, pos=(1,2), span=(1,1), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.down_button, pos=(2,0), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(150, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)        
        
        
class GrismPanel(wx.Panel):
    """This panel controls the Grism wheel"""
    def __init__(self, parent, *args, **kwargs):
        super(GrismPanel, self).__init__(parent) 
        
        self.parent = parent

        # Attributes        
        self.grism = ['j', 'h', 'k', 'Open']
    
        self.curr_grism_text = wx.StaticText(self, label="Current Grism:")
        self.curr_grism = wx.StaticText(self, label="Checking...")
        self.select_button = wx.Button(self, label="Select")
        self.grism_choice = wx.ComboBox(self, -1, size=(100,-1), choices=self.grism, style=wx.CB_READONLY)
    
        # Layout
        self.__DoLayout()
        # Event handlers
        self.Bind(wx.EVT_COMBOBOX, self.on_select, self.grism_choice)
        self.Bind(wx.EVT_BUTTON, self.move_grism, self.select_button)
        
    def __DoLayout(self):
        ## Layout for this panel:
        ##
        ##    0                      1
        ##   +--------------------+---------------------+
        ## 0 |  curr_filter_text  |   curr_filter       |
        ##   +-------------------+----------------------+
        ## 1 |   select_button   |    filter_choice     |
        ##   +-------------------+----------------------+
        
        sbox = wx.StaticBox(self, label="Grism")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.curr_grism_text,  pos=(0,0), flag=wx.ALIGN_LEFT)
        sizer.Add(self.curr_grism,  pos=(0,1), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.grism_choice, pos=(1,0), flag=wx.ALIGN_CENTER)
        sizer.Add(self.select_button, pos=(1,1), flag=wx.ALIGN_CENTER)
    
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(200, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        
    def on_select(self, event):
        try:
            selected = event.GetSelection()
            pub.sendMessage("LOG EVENT", "Chosen Grism is..." + str(self.grism[selected]))
            return selected
        except ValueError:
            pass

    def move_grism(self, event):
        try:
            pub.sendMessage("LOG EVENT", "Moving to Grism...")
            selected = self.grism_choice.GetSelection()
            self.curr_grism.SetLabel(self.grism[selected])
        except ValueError:
            pass        

class GuidePanelSettings(wx.Panel):
    """This panel controls the guide camera settings"""
    def __init__(self, parent, *args, **kwargs):
        super(GuidePanelSettings, self).__init__(parent)
 
        self.parent = parent
        #Is the camera connected and ready to go
        self.c_power = False
        #is the guiding log turned on
        self.guide_log_status = False
        #current status of the camera
        self.status = None
        #current status of guiding
        self.guidestatus = threading.Event()
        #current status of image sequence
        self.seriesstatus = threading.Event()
        #True if waiting for camera to show up on USB bus
        self.looking = True
        #camera instance
        self.cam0 = None
                
        #guide
        self.star1 = wx.StaticText(self, label="Star 1: ")
        self.star2 = wx.StaticText(self, label="Star 2: ")
        self.star1_xy = wx.StaticText(self, label="(x.000,y.000)")
        self.star2_xy = wx.StaticText(self, label="(x.000,y.000)")
        self.guide = wx.ToggleButton(self, 1, size=(100,-1), label="Guiding Off")
        self.log_onoff = wx.CheckBox(self, -1, 'Guiding Log On', (10,10))
        self.guide_state = self.guide.GetValue()
        self.cadence_text = wx.StaticText(self, label="Cadence (s): ")
        self.cadence = wx.TextCtrl(self, -1, '10.0', size=(50,-1), style=wx.TE_NO_VSCROLL)
                
        #stat
        self.curr_temp_text = wx.StaticText(self, label="Current Temp: ")
        self.curr_temp = wx.StaticText(self, label="...              ")
        self.curr_setpoint_text = wx.StaticText(self, label="Current Set Point (C): ")
        self.curr_setpoint = wx.TextCtrl(self, -1, '', size=(50,-1), style=wx.TE_NO_VSCROLL)
        self.curr_setpoint.SetValue('0')
        self.curr_setpoint_button = wx.Button(self, size=(80,-1), label="Set")
        
        #exp
        self.exp_text = wx.StaticText(self, -1, label="Exposure (s):")
        self.exposure = wx.TextCtrl(self, -1, '', size=(50,-1), style=wx.TE_NO_VSCROLL)
        self.exposure.SetValue('0.25')
        self.take = wx.Button(self, size=(100, -1), label="Take Image")
        self.bin_text = wx.StaticText(self, -1, label="Bin (NxN): ")
        self.bin = wx.SpinCtrl(self, id=-1, value='', min=1, max=4, initial=1, size=(40, -1))
               
        self.series = wx.SpinCtrl(self, id=-1, value='', min=1, max=1000, initial=3, size=(50, -1))
        self.series_text = wx.StaticText(self, -1, label="Series: ")
        self.scadence_text = wx.StaticText(self, -1, label="Cadence (s):")
        self.scadence = wx.TextCtrl(self, -1, '', size=(50,-1), style=wx.TE_NO_VSCROLL)
        self.scadence.SetValue('2.0')
        self.take_series = wx.ToggleButton(self, 2, size=(100, -1), label="Take Series")
        self.sname = wx.TextCtrl(self, -1, 'img', size=(130,-1), style=wx.TE_NO_VSCROLL)
        self.sname_text = wx.StaticText(self, -1, label="Series Name: ")
        self.autosave_on_text = wx.StaticText(self, label="Autosave: ")
        self.autosave_cb = wx.CheckBox(self, -1, " " , (10,10))
        self.autosave_cb.SetValue(False)
        
        self.rb_light = wx.RadioButton(self, -1, 'Light', (10, 10), style=wx.RB_GROUP)
        self.rb_dark = wx.RadioButton(self, -1, 'Dark', (10, 30))
        self.rb_flat = wx.RadioButton(self, -1, 'Flat', (10, 50))
        
        # Layout
        self.__DoLayout()
        
        # Event Handlers
        
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnGuide, id=1)
        self.Bind(wx.EVT_BUTTON, self.Expose, self.take)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.ExposeSeries, id=2)
        self.Bind(wx.EVT_BUTTON, self.SetPoint, self.curr_setpoint_button)
        
        self.Bind(wx.EVT_CHECKBOX, self.GuideLog, self.log_onoff)
        
        self.Bind(wx.EVT_SPINCTRL, self.Bin, self.bin)

        # Start up image display
        self.d = ds9.ds9()
        self.d.set("width 538")
        self.d.set("height 528")
        # Look for camera and initialize it
        self.__OnPower()
        
    def __OnPower(self):
        startlook = time.time()
        while self.looking:
            dev = usb.core.find(idVendor=0x0f18, idProduct=0x000a)
            if DEBUG: print dev
            
            if dev is None:
                time.sleep(0.5)
                if DEBUG: print time.time()
                if time.time()-startlook > 5:
                    self.looking = False
                    break
            if dev != None:
                self.looking = False
                self.c_power = True
                cams = FLI.camera.USBCamera.find_devices()
                self.cam0 = cams[0]
                self.cam0.set_bit_depth("16bit")
                temp = self.cam0.get_temperature()
                self.curr_temp.SetLabel(str(temp) + u'\N{DEGREE SIGN}' + 'C  ')
                
    def OffPower(self):
        self.c_power = False
        self.looking = True
        self.curr_temp.SetLabel('...')
        self.c.shutdown()
        self.c = None
        
    def __DoLayout(self):
        # make sizers
        guide_sz   = wx.GridBagSizer(vgap=3, hgap=3)
        stat_sz    = wx.GridBagSizer(vgap=3, hgap=3)
        exp_sz     = wx.GridBagSizer(vgap=3, hgap=3)
                        
        # add attributes to sizers
        exp_sz.Add(self.exp_text, pos=(0,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        exp_sz.Add(self.exposure, pos=(0,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        exp_sz.Add(self.take, pos=(0,2), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        exp_sz.Add(self.bin_text, pos=(0,3), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        exp_sz.Add(self.bin, pos=(0,4), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        
        exp_sz.Add(self.series_text, pos=(1,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        exp_sz.Add(self.series, pos=(1,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        exp_sz.Add(self.scadence_text, pos=(2,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        exp_sz.Add(self.scadence, pos=(2,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)        
        exp_sz.Add(self.sname_text, pos=(3,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        exp_sz.Add(self.sname, pos=(3,1), span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        exp_sz.Add(self.autosave_on_text, pos=(3,3), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        exp_sz.Add(self.take_series, pos=(1,2), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        exp_sz.Add(self.autosave_cb, pos=(3,4), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        
        exp_sz.Add(self.rb_light, pos=(4,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        exp_sz.Add(self.rb_dark, pos=(4,2), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        exp_sz.Add(self.rb_flat, pos=(4,3), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
                      
        guide_sz.Add(self.star1, pos=(0,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        guide_sz.Add(self.star2, pos=(1,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        guide_sz.Add(self.star1_xy, pos=(0,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        guide_sz.Add(self.star2_xy, pos=(1,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        guide_sz.Add(self.guide, pos=(2,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        guide_sz.Add(self.log_onoff, pos=(3,0), span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        guide_sz.Add(self.cadence_text, pos=(4,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        guide_sz.Add(self.cadence, pos=(4,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                
        stat_sz.Add(self.curr_temp_text, pos=(1,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        stat_sz.Add(self.curr_temp, pos=(1,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        stat_sz.Add(self.curr_setpoint_text, pos=(2,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        stat_sz.Add(self.curr_setpoint, pos=(2,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        stat_sz.Add(self.curr_setpoint_button, pos=(2,2), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
                        
        # Set up master StaticBox
        sbox = wx.StaticBox(self, label="Guide Camera")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=5, hgap=5)      
        
        # add sizers to master sizer
        sizer.Add(exp_sz,       pos=(0,0), span=(1,3))
        sizer.Add(wx.StaticLine(self),   pos=(1,0), span=(1,3), flag=wx.EXPAND|wx.BOTTOM)
        sizer.Add(stat_sz,      pos=(2,0), span=(1,1))
        sizer.Add(wx.StaticLine(self, -1, style=wx.LI_VERTICAL),   pos=(2,1), span=(1,1), flag=wx.EXPAND)
        sizer.Add(guide_sz,     pos=(2,2), span=(1,1), flag=wx.EXPAND)
        
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        
        # Set up a timer to update camera info
        TIMER_ID = 130 # Random number; it doesn't matter
        self.timer = wx.Timer(self, TIMER_ID)
        self.timer.Start(10000) # poll every 20 seconds
        wx.EVT_TIMER(self, TIMER_ID, self.on_timer)

    def on_timer(self, event):
        try:
            if not self.c_power:
                pass
            else:
                #get current temp
                temp = self.cam0.get_temperature()
                self.curr_temp.SetLabel(str(temp) + u'\N{DEGREE SIGN}' + 'C  ')
                            
        except ValueError:
            pass
        
    @threadtools.callafter
    def DisplayImage(self, event, image):
        image[:] = np.fliplr(image)[:]
        self.d.set_np2arr(image)
        self.d.set("zoom to fit")
        
    def updateKeywords(self):
        """Update the keywords for the FITS file header"""
        global keywords
#        #TelescopePanel.scope_update(self.parent.TelescopePanel)
        if self.rb_light.GetValue():
            light = True
            keywords["IMGTYPE"] = "Light"
        if self.rb_dark.GetValue():
            light = False
            keywords["IMGTYPE"] = "Dark"
        if self.rb_flat.GetValue():
            light = True
            keywords["IMGTYPE"] = "Flat"
        #get name for header
        name = self.sname.GetValue()

        keywords["OBSERVER"] = str(self.parent.parent.GetPage(3).observerTxt.GetValue())
        keywords["FILENAME"] = str(self.sname.GetValue())
        keywords["RA"]       = 0
        keywords["DEC"]      = 0
        keywords["AIRMASS"]  = 0 
        keywords["TELALT"]   = 0 
        keywords["TELAZ"]    = 0
        keywords["TELFOCUS"] = 0 
        keywords["PA"]       = 0 
        keywords["JD"]       = 0 
        keywords["GDATE"]    = 0 
        keywords["WINDVEL"]  = 0 
        keywords["WINDGUST"] = 0 
        keywords["WINDDIR"]  = 0 
        keywords["REI12"]    = 0 
        keywords["REI34"]    = 0 
        keywords["MASK"]     = 0
        keywords["FILTER1"]  = 0 
        keywords["FILTER2"]  = 0
        keywords["GRISM"]    = 0
        keywords["EXP"]      = float(self.exposure.GetValue())
        keywords["CAMTEMP"]  = float(self.cam0.get_temperature())
        keywords["CRPIX1"]   = 0
        keywords["CRPIX2"]   = 0
        keywords["CDELT1"]   = float(self.parent.parent.GetPage(3).pixelscalexTxt.GetValue())
        keywords["CDELT2"]   = float(self.parent.parent.GetPage(3).pixelscaleyTxt.GetValue())
        keywords["CRVAL1"]   = 0
        keywords["CRVAL2"]   = 0
        keywords["CROTA2"]   = 0

    def updateHeader(self, fitsfile):
        """Update the header of the fits file to be saved"""
        
            
    def Expose(self, event):
        """take an exposure with current settings"""
        # Set exposure time
        self.cam0.set_exposure(int(1000*float(self.exposure.GetValue())))
        # Update header info
        self.updateKeywords()
        # take image
        self.image = self.cam0.take_photo()
        
#        self.fits = pic.UpdateFitsHeader(self.fits, keywords, name)
        #send image to the display
        self.DisplayImage(event, self.image)
        autosave = self.autosave_cb.GetValue()
        if autosave:
            # Make Fits File
            filename = keywords["FILENAME"]
            ftime = keywords["GDATE"]
            hdu = pyfits.PrimaryHDU(self.image)
            hdulist = pyfits.HDUList([hdu])
            hdulist.writeto(str(self.parent.parent.GetPage(3).savefolderTxt.GetValue())+filename+ftime+".fits")
            
            
    def ExposeSeries(self, event):
        if self.take_series.GetValue():
            pub.sendMessage("LOG EVENT", "Image Series Started...")
            scount = self.series.GetValue()
            scadence = self.scadence.GetValue()
            self.take_series.SetLabel("Cancel")
            self.take_series.SetForegroundColour((34,139,34))
            self.exp_series_thread = SeriesExpThread(self, event, scount, scadence)
            self.exp_series_thread.daemon=True
            self.seriesstatus.set()
            self.exp_series_thread.start()
        else:
            self.SeriesCancel("Series Stopped...")
#            pub.sendMessage("LOG EVENT", "Series Stopped...")
#            self.take_series.SetLabel("Take Series")
#            self.take_series.SetForegroundColour((0,0,0))
#            self.seriesstatus.clear()
#            self.exp_series_thread.join()
            
    def Bin(self, event):
        h = self.bin.GetValue()
        self.cam0.set_image_binning(h,h)
        
    def SetPoint(self, event):
        temp = int(self.curr_setpoint.GetValue())
        self.cam0.set_temperature(temp)
                
    def ChooseStar1(self, event):
        global s1
        s1 = event.GetPosition()
        #display PyGuide coordinate system
            
        self.pgcoord = pic.scale_coord_to_cam(s1, self.max_size, self.roiH.GetValue())
        self.pgcoord = pic.coord_flip(self.pgcoord,self.roiH.GetValue())
        if DEBUG: print 's1', s1, 'roiH', self.roiH.GetValue()
        self.star1_xy.SetLabel(str(self.pgcoord))
        self.DisplayImage(event, self.image)
        
    def ChooseStar2(self, event):
        global s2
        s2 = event.GetPosition()
        self.star2_xy.SetLabel(str(s2))
        self.DisplayImage(event, self.image)
    
    def OnGuide(self, event):
        try:
            if not self.c_power:
                wx.Bell()
                wx.MessageBox('The guide camera does not have power.', style=wx.OK|wx.CENTER)
                self.guide.SetValue(False)
            else:
                if self.guide.GetValue(): 
                    pub.sendMessage("LOG EVENT", "Guiding Started...")
                    self.guide.SetLabel("Guiding On")
                    self.guide.SetForegroundColour((34,139,34))
                    #get variables to pass to guide routine
                    cadence = float(self.cadence.GetValue())
                    if DEBUG: print cadence
                    self.guide_thread = GuideThread(self, self.pgcoord , cadence)
                    self.guide_thread.daemon=True
                    self.guidestatus.set()
                    self.guide_thread.start()
                else:
                    pub.sendMessage("LOG EVENT", "Guiding Stopped...")
                    self.guide.SetLabel("Guiding Off")
                    self.guide.SetForegroundColour((0,0,0))
                    self.guidestatus.clear()
                    self.guide_thread.join()
                    
        except ValueError:
            pass
    
    @threadtools.callafter
    def GuideError(self, error):
        pub.sendMessage("LOG EVENT", error)
        self.guide.SetLabel("Guiding Off")
        self.guide.SetForegroundColour((0,0,0))
        self.guide.SetValue(False)
        self.guidestatus.clear()
        self.guide_thread.join()
        wx.Bell()
        wx.MessageBox(error, style=wx.OK|wx.CENTER)

    @threadtools.callafter
    def Update(self, shift, currentxy):
        pub.sendMessage("shiftupdate", shift)
        pub.sendMessage("xyupdate", currentxy)
        
    @threadtools.callafter
    def SeriesUpdate(self, image, total):
        pub.sendMessage("change_statusbar", "Image " + str(image+1) + " of " + str(total)) 
        
    @threadtools.callafter
    def SeriesCancel(self, error):
        pub.sendMessage("LOG EVENT", error)
        pub.sendMessage("change_statusbar", error)
        self.take_series.SetLabel("Take Series")
        self.take_series.SetForegroundColour((0,0,0))
        self.take_series.SetValue(False)
        self.seriesstatus.clear()
        self.exp_series_thread.join()
        
    def GuideLog(self, event):
        if self.log_onoff.GetValue():
            self.guide_log_status = True
            pub.sendMessage("LOG EVENT", 'Guide Logging On')
        else:
            self.guide_log_status = False
            pub.sendMessage("LOG EVENT", 'Guide Logging Off')
            pass

class GuidePlotPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super(GuidePlotPanel, self).__init__(parent)
        self.parent = parent
        self.data1 = []
        self.data2 = [] 
        
        self.__DoLayout()

    def __DoLayout(self):
        self.init_plot()
        self.canvas = FigCanvas(self, -1, self.fig)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)        
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        #self.SetBackgroundColour(panelcolor)

        #subscribe to xy updates
        pub.subscribe(self.data_update, "shiftupdate")

      
    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((2.0, 2.0), dpi=self.dpi, facecolor='0.9')
        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_bgcolor('black')
        self.axes.set_title(r'Guiding Corrections: cyan + $\rightarrow$ x magenta * $\rightarrow$ y', size=8)
        self.axes.set_ylabel('Pixels', size=8)
        self.axes.set_xlabel('Seconds', size=8)
        
        pylab.setp(self.axes.get_xticklabels(), fontsize=6)
        pylab.setp(self.axes.get_yticklabels(), fontsize=6)

        # plot the data as a line series, and save the reference 
        # to the plotted line series
        self.plot_data1 = self.axes.plot(self.data1, 'c+')[0]
        self.plot_data2 = self.axes.plot(self.data2, 'm*')[0]

    def draw_plot(self):
        """ Redraws the plot
        """
        # when xmin is on auto, it "follows" xmax to produce a 
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        #
        xmax = len(self.data1) if len(self.data1) > 50 else 50
        xmin = xmax - 50
        
        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        # 
        # note that it's easy to change this scheme to the 
        # minimal/maximal value in the current display, and not
        # the whole data set.
        # 
        ymin = round(min(min(self.data1),min(self.data2)), 0) - 0.5
        ymax = round(max(max(self.data1),max(self.data2)), 0) + 0.5
        
        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)
        
        # anecdote: axes.grid assumes b=True if any other flag is
        # given even if b is set to False.
        # so just passing the flag into the first statement won't
        # work.
        #
        self.axes.grid(True, color='gray')
        #self.axes.grid(False)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly 
        # iterate, and setp already handles this.
        #  
        pylab.setp(self.axes.get_xticklabels(), 
            visible=True)
        
        self.plot_data1.set_xdata(np.arange(len(self.data1)))
        self.plot_data1.set_ydata(np.array(self.data1))
        self.plot_data2.set_xdata(np.arange(len(self.data2)))
        self.plot_data2.set_ydata(np.array(self.data2))
        
        self.canvas.draw()
    
    def data_update(self, msg):
        print "xshift: ", msg.data[0][0], " yshift: ", msg.data[0][1]
        #add new data
        self.data1.append(msg.data[0][0])
        self.data2.append(msg.data[0][1])
        
        self.draw_plot()
        
    def data_clear(self):
        self.data1 = [0]
        self.data2 = [0]
        self.draw_plot()
        
class GuideInfoPanel(wx.Panel):
    """This panel shows information on the guide camera system."""
    def __init__(self, parent, *args, **kwargs):
        super(GuideInfoPanel, self).__init__(parent)

        self.parent = parent
        
        # Attributes 
        self.curr_centroids_text = wx.StaticText(self, label="Current Centroids: ")
        self.curr_centroids = wx.StaticText(self, label="s1 = (0,0)  s2 = (0,0)")
        
        self.plotCanvas = GuidePlotPanel(self)
        self.reset = wx.Button(self, size=(50,-1), label="Reset Plot")
        #self.guide_hist = wx.StaticBitmap(self)
        #self.guide_hist.SetFocus()
        #self.guide_hist.SetBitmap(wx.Bitmap('guide_err.png'))
        # Layout
        self.__DoLayout()
        
        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.ResetPlot, self.reset)

    def __DoLayout(self):
        ## Layout for this panel:
        ##
        ##    0               1
        ##   +---------------+---------------+
        ## 0 | curr_ra_text  | self.curr_ra  |
        ##   +---------------+---------------+
        ## 1 | curr_dec_text | self.new_dec  |
        ##   +---------------+---------------+
        ##
        sbox = wx.StaticBox(self, label="Guide Status")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)
        
        # Add controls to gridbag
        sizer.Add(self.curr_centroids_text, pos=(0,0), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_centroids, pos=(0,1), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.plotCanvas, pos=(2,0), span=(10,4), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND)
        sizer.Add(self.reset, pos=(1,0), span=(1,1), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND)
        
        #sizer.Add(self.guide_hist, pos=(3,0), span=(1,2), flag=wx.ALIGN_CENTER_HORIZONTAL)
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(300, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        
        #subscribe to xy updates
        pub.subscribe(self.UpdatePanel, "xyupdate")


    def ResetPlot(self, event):
        self.plotCanvas.data_clear()
    
    def UpdatePanel(self, s1centroid):
        print s1centroid.data[0], s1centroid.data[1]
        self.curr_centroids.SetLabel('s1=('+ str(round(s1centroid.data[0], 2))+','+ str(round(s1centroid.data[1],2))+'), s2=(0,0)')
                                 

class KmirrorPanel(wx.Panel):
    """This panel shows information and controls relevant to the Kmirror.

    Current PA: Shows the PA of the Kmirror in degrees CW from 0.
        New PA: A new angle to move the Kmirror.
          Move: Tell the Kmirror to go to the New PA.
          
    """
    def __init__(self, parent, *args, **kwargs):
        #wx.Panel.__init__(self, parent, *args, **kwargs)
        super(KmirrorPanel, self).__init__(parent)

        self.parent = parent
                
        #global k = None
        self.k_power = False        
        self.trackstatus = True
        
        # Attributes
        self.curr_pa_text = wx.StaticText(self, label="Current PA:")
        self.curr_pa = wx.StaticText(self, label="...")
        self.new_pa_text = wx.StaticText(self, label="New PA:")
        self.new_pa = wx.TextCtrl(self, size=(62,-1))

        self.step_p = wx.Button(self, size=(30,-1), label="+")
        self.step_m = wx.Button(self, size=(30,-1), label="-")
        self.track_button = wx.Button(self,  size=(62,-1), label="Track")
        self.set_button = wx.Button(self,  size=(62,-1), label="Set")
        self.stop_button = wx.Button(self,  size=(62,-1), label="Stop")
        self.home_button = wx.Button(self, size=(62,-1), label="Home")
        self.mode_txt = wx.StaticText(self, label="Mode:")
        self.mode = wx.ComboBox(self, -1, size=(126,-1), choices=("Position Angle", "Vertical Angle", "Stationary"), style=wx.CB_READONLY)
        
        self.step_txt = wx.StaticText(self, label="Step Size:")
        self.step_size = wx.SpinCtrl(self, -1, '', (0.1, 5), (62, -1))
        self.step_size.SetRange(1, 5)
        self.step_size.SetValue(1)
                
        # Layout
        self.__DoLayout()
        
        # Event handlers
        self.Bind(wx.EVT_BUTTON, self.step_pos, self.step_p)
        self.Bind(wx.EVT_BUTTON, self.step_neg, self.step_m)
        self.Bind(wx.EVT_BUTTON, self.on_track, self.track_button)
        self.Bind(wx.EVT_BUTTON, self.on_set, self.set_button)
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.stop_button)
    
    def OnPower(self):
        self.k_power = True
        global k 
        k = Kmirror()
    
    def OffPower(self):
        self.k_power = False
        self.curr_pa.SetLabel('...')
        k.__del__()
        
    def __DoLayout(self):
        ## Layout for this panel:
        ##
        ##    0               1
        ##   +---------------+---------------+
        ## 0 | curr_pa_text  | self.curr_pa  |
        ##   +---------------+---------------+
        ## 1 | new_pa_text   | self.new_pa   |
        ##   +---------------+---------------+
        ## 2 |         move_button           |
        ##   +---------------+---------------+
        ## 3 |  track_button |  stop_button  |
        ##   +---------------+---------------+
        sbox = wx.StaticBox(self, label="Kmirror")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        # Add controls to gridbag
        sizer.Add(self.curr_pa_text, pos=(0,0), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.curr_pa, pos=(0,1), flag=wx.ALIGN_LEFT)

        sizer.Add(self.new_pa_text,  pos=(1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.new_pa,  pos=(1,1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.set_button,  pos=(1,2), span=(1,2), flag=wx.ALIGN_LEFT)
        
        sizer.Add(self.step_m, pos=(2,2), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.step_p, pos=(2,3), flag=wx.ALIGN_LEFT)
        
        sizer.Add(self.step_txt, pos=(2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.step_size, pos=(2,1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.track_button,  pos=(3,0), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.stop_button,  pos=(3,1), flag=wx.ALIGN_LEFT)
        sizer.Add(self.home_button,  pos=(3,2), span=(1,2), flag=wx.ALIGN_LEFT)
        
        sizer.Add(self.mode_txt,  pos=(4,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.mode, pos=(4,1), span=(1,3), flag=wx.ALIGN_LEFT)

        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(200, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        
        # Set up a timer to update the current position angle
        TIMER_ID = 100 # Random number; it doesn't matter
        self.timer = wx.Timer(self, TIMER_ID)
        self.timer.Start(2000) # poll every 5 seconds
        wx.EVT_TIMER(self, TIMER_ID, self.on_timer)

    def on_set(self, event):
        try:
            if not self.k_power:
                wx.Bell()
                wx.MessageBox('The rotator does not have power.', style=wx.OK|wx.CENTER)
            else:
                pa = float(self.new_pa.GetValue())
                pub.sendMessage("LOG EVENT", "Rotator: Move to %d" % (int(pa)%360) + u'\N{DEGREE SIGN}')
                k.set_pa(pa)
                pub.sendMessage("LOG EVENT", "Rotator: Is at %d" % (int(pa)%360) + u'\N{DEGREE SIGN}')
        except ValueError:
            pass # TODO: Error Message

    def on_track(self, event):
        try:
            if not self.k_power:
                wx.Bell()
                wx.MessageBox('The rotator does not have power.', style=wx.OK|wx.CENTER)
            else:
                pub.sendMessage("LOG EVENT", "K-Mirror is Tracking...")
                self.trackstatus = True
                self.track_thread = TrackThread(self)
                self.track_thread.daemon=True
                self.track_thread.start()
            
        except ValueError:
            pass

    def on_stop(self, event):
        try:
            if not self.k_power:
                wx.Bell()
                wx.MessageBox('The rotator does not have power.', style=wx.OK|wx.CENTER)
            else:
                pub.sendMessage("LOG EVENT", "K-Mirror Stopped...")
                self.trackstatus = False
        except ValueError:
            pass

    def on_timer(self, event):
        try:
            if not self.k_power:
                pass
            else:
                pa = k.get_pa()
                self.curr_pa.SetLabel(str(pa) + u'\N{DEGREE SIGN}')
        except ValueError:
            pass
    
    def step_pos(self, event):
        try:
            if not self.k_power:
                wx.Bell()
                wx.MessageBox('The rotator does not have power.', style=wx.OK|wx.CENTER)
            else:
                step = self.step_size.GetValue()
                pa = k.get_pa() + step
                pub.sendMessage("LOG EVENT", "Stepping rotator +")
                k.set_pa(pa)
                pub.sendMessage("LOG EVENT", "Rotator moved +" + str(step))
        except ValueError:
            pass

    def step_neg(self, event):
        try:
            if not self.k_power:
                wx.Bell()
                wx.MessageBox('The rotator does not have power.', style=wx.OK|wx.CENTER)
            else:
                step = self.step_size.GetValue()
                pa = k.get_pa() - step
                pub.sendMessage("LOG EVENT", "Stepping rotator -")
                k.set_pa(pa)
                pub.sendMessage("LOG EVENT", "Rotator moved -" + str(step))
        except ValueError:
            pass

class MaskPanel(wx.Panel):
    """This panel controls the mask wheel."""
    def __init__(self, parent, *args, **kwargs):
        super(MaskPanel, self).__init__(parent) 
        
        self.parent = parent

        # Attributes        
        self.masks = ['Field 1', 'Field 2', 'Field 3', 'Field 4', 'Open', 'Dark']#settings.mask 
        
        self.curr_mask_text = wx.StaticText(self, label="Current Mask:")
        self.curr_mask = wx.StaticText(self, label="Checking...")
        self.select_button = wx.Button(self, label="Select")
        self.mask_choice = wx.ComboBox(self, -1, size=(100,-1), choices=self.masks, style=wx.CB_READONLY)
        
        # Layout
        self.__DoLayout()
        
        # Event handlers
        self.Bind(wx.EVT_COMBOBOX, self.on_select, self.mask_choice)
        self.Bind(wx.EVT_BUTTON, self.move_mask, self.select_button)
        
    def __DoLayout(self):
        ## Layout for this panel:
        ##
        ##    0                      1
        ##   +--------------------+---------------------+
        ## 0 |  curr_mask_text   |   curr_mask          |
        ##   +-------------------+----------------------+
        ## 1 |   select_button   |    mask_choice       |
        ##   +-------------------+----------------------+
        
        sbox = wx.StaticBox(self, label="Mask Wheel")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        # Add controls to gridbag
        sizer.Add(self.curr_mask_text,  pos=(0,0), flag=wx.ALIGN_LEFT)
        sizer.Add(self.curr_mask,  pos=(0,1), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.mask_choice, pos=(1,0), flag=wx.ALIGN_CENTER)
        sizer.Add(self.select_button, pos=(1,1), flag=wx.ALIGN_CENTER)
    
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(200, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
       
    def on_select(self, event):
        try:
            selected = event.GetSelection()
            pub.sendMessage("LOG EVENT", "Chosen mask is..." + self.masks[selected])
            return selected
        except ValueError:
            pass

    def move_mask(self, event):
        try:
            pub.sendMessage("LOG EVENT", "Moving to mask...")
            selected = self.mask_choice.GetSelection()
            print selected
            maskchoice = 'setINDI "FLI Wheel.FILTER_SLOT.FILTER_SLOT_VALUE=5"'
            print maskchoice
            #mask = subprocess.Popen(maskchoice, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #stdout_text, stderr_text = mask.communicate()
            #print stdout_text, stderr_text
            self.curr_mask.SetLabel(self.masks[selected])
        except ValueError:
            pass

class SchematicPanel(wx.Panel):
    """This panel shows the NESSI instrument diagram."""
    def __init__(self, parent, *args, **kwargs):
        super(SchematicPanel, self).__init__(parent)
        
        self.parent = parent
        # Attributes
        self.schematic = wx.StaticBitmap(self)
        self.schematic.SetFocus()
        self.schematic.SetBitmap(wx.Bitmap('media/nessi_fullimage.png'))
        
        # Layout
        self.__DoLayout()
        
        # Event handlers
        
    def __DoLayout(self):
        ## Layout for this panel:
        ##    0               
        ##   +---------------+
        ## 0 |     Logo      |
        ##   +---------------+
        sbox = wx.StaticBox(self, label="")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.schematic, pos=(0,0), flag=wx.ALIGN_CENTER)
        
        # Add the grid bag to the static box and make everything fit
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        
class PageOne(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super(PageOne, self).__init__(parent)
        
        # Attributes
        self.Schematic = SchematicPanel(self)
        self.Mask = MaskPanel(self)
        self.FilterOne = FilterPanelOne(self)
        self.FilterTwo = FilterPanelTwo(self)
        self.Grism = GrismPanel(self)
        self.Kmirror = KmirrorPanel(self)
        self.GuideInfo = GuideInfoPanel(self)
        self.FocusREI12 = FocusREI12(self)
        self.FocusREI34 = FocusREI34(self)
        
        self.__DoLayout()

    def __DoLayout(self):
        ## Layout for this panel:
        ##
        ##    0               1
        ##   +---------------+---------------+
        ## 0 | k-mirror      | guiding       |
        ##   +---------------+---------------+
        ## 1 | schematic     | self.new_dec  |
        ##   +---------------+---------------+
        ##
        sbox = wx.StaticBox(self, label="")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)
        
        # Add controls to gridbag
        sizer.Add(self.Kmirror, pos=(0,0), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.FocusREI12, pos=(0,1), span=(1,1), flag=wx.LEFT|wx.ALIGN_BOTTOM)
        sizer.Add(self.GuideInfo, pos=(1,2), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.Schematic, pos=(1,0), span=(6,2), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.FocusREI34, pos=(2,2), span=(1,1), flag=wx.LEFT|wx.ALIGN_BOTTOM)
        sizer.Add(self.Mask, pos=(3,2), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.FilterOne, pos=(4,2), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.FilterTwo, pos=(5,2), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.Grism, pos=(6,2), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
                
        
        # Add the grid bag to the static box and make everything fit
        boxSizer.Add(sizer, wx.EXPAND)
        self.SetSizerAndFit(boxSizer)
        
        
class PageTwo(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super(PageTwo, self).__init__(parent)
        
        # Attributes
        self.t = wx.StaticText(self, -1, "K-Mirror Control", (40,40))

        self.__DoLayout()

    def __DoLayout(self):
        sbox = wx.StaticBox(self, label="")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)
        
        # Add controls to gridbag
        sizer.Add(self.t, pos=(0,0), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
                
        # Add the grid bag to the static box and make everything fit
        boxSizer.Add(sizer, wx.EXPAND)
        self.SetSizerAndFit(boxSizer)

class PageThree(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super(PageThree, self).__init__(parent)
        
        # Attributes
        self.Guide = GuidePanelSettings(self)
        self.parent = parent        
        self.__DoLayout()

    def __DoLayout(self):
        ## Layout for this panel:
        ##
        ##    0               1
        ##   +---------------+---------------+
        ## 0 | k-mirror      | guiding       |
        ##   +---------------+---------------+
        ## 1 | schematic     | self.new_dec  |
        ##   +---------------+---------------+
        ##
        sbox = wx.StaticBox(self, label="")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)
        
        # Add controls to gridbag
        sizer.Add(self.Guide, pos=(0,0), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
                
        # Add the grid bag to the static box and make everything fit
        boxSizer.Add(sizer, wx.EXPAND)
        self.SetSizerAndFit(boxSizer)

class PageFour(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super(PageFour, self).__init__(parent)
        
        # Attributes
                
        self.scopeLbl = wx.StaticText(self, wx.ID_ANY, "Telescope Server:")
        self.scopeTxt = wx.TextCtrl(self, wx.ID_ANY, "")
        self.scopeTxt.Disable()
 
        self.scopeportLbl = wx.StaticText(self, wx.ID_ANY, "Telescope Port:")
        self.scopeportTxt = wx.TextCtrl(self, wx.ID_ANY, "")
        self.scopeportTxt.Disable()
 
        self.savefolderLbl = wx.StaticText(self, wx.ID_ANY, "Save Folder:")
        self.savefolderTxt = wx.TextCtrl(self, wx.ID_ANY, "")
        self.savefolderTxt.Disable()
 
        self.instportLbl = wx.StaticText(self, wx.ID_ANY, "Instrument Port:")
        self.instportTxt = wx.TextCtrl(self, wx.ID_ANY, "")
        self.instportTxt.Disable()
        
        self.pixelscalexLbl = wx.StaticText(self, wx.ID_ANY, "Guide Camera Pixel Scale X (deg/pixel):")
        self.pixelscalexTxt = wx.TextCtrl(self, wx.ID_ANY, "")
        self.pixelscalexTxt.Disable()
        
        self.pixelscaleyLbl = wx.StaticText(self, wx.ID_ANY, "Guide Camera Pixel Scale Y (deg/pixel):")
        self.pixelscaleyTxt = wx.TextCtrl(self, wx.ID_ANY, "")
        self.pixelscaleyTxt.Disable()
        
        self.observerLbl = wx.StaticText(self, wx.ID_ANY, "Observer:")
        self.observerTxt = wx.TextCtrl(self, wx.ID_ANY, "")
        self.observerTxt.Disable()
        
        self.editbtn = wx.Button(self, label="Edit")
        self.editadvbtn = wx.Button(self, label="Advanced")
        self.savebtn = wx.Button(self, label="Save")
        
        self.widgets = [self.savefolderTxt, self.instportTxt, self.pixelscalexTxt, self.pixelscaleyTxt, self.observerTxt]
        self.advwidgets = [self.scopeTxt, self.scopeportTxt, self.savefolderTxt, self.instportTxt, self.pixelscalexTxt, self.pixelscaleyTxt, self.observerTxt]
        
        # Layout
        self.__DoLayout()

        # Handlers
        self.Bind(wx.EVT_BUTTON, self.editPreferences, self.editbtn)
        self.Bind(wx.EVT_BUTTON, self.editAdvPreferences, self.editadvbtn)
        self.Bind(wx.EVT_BUTTON, self.savePreferences, self.savebtn)
   
    def __DoLayout(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        prefSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        prefSizer.AddGrowableCol(1)
 
        prefSizer.Add(self.scopeLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.scopeTxt, 0, wx.EXPAND)
        prefSizer.Add(self.scopeportLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.scopeportTxt, 0, wx.EXPAND)
        prefSizer.Add(self.savefolderLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.savefolderTxt, 0, wx.EXPAND)
        prefSizer.Add(self.instportLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.instportTxt, 0, wx.EXPAND)
        prefSizer.Add(self.pixelscalexLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.pixelscalexTxt, 0, wx.EXPAND)
        prefSizer.Add(self.pixelscaleyLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.pixelscaleyTxt, 0, wx.EXPAND)
        prefSizer.Add(self.observerLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.observerTxt, 0, wx.EXPAND)
        prefSizer.Add(self.editbtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.savebtn, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.editadvbtn, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
                
        mainSizer.Add(prefSizer, 0, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(mainSizer)
 
        # ---------------------------------------------------------------------
        # load preferences
        self.loadPreferences()
 
    #----------------------------------------------------------------------
    def loadPreferences(self):
        """
        Load the preferences and fill the text controls
        """
        config = prefcontrol.getConfig()
        scope = config['scope server']
        scopeport = config['scope port']
        savefolder = config['savefolder']
        instport = config['instrument port']
        pixelscalex = config['pixel scale x']
        pixelscaley = config['pixel scale y']
        observer = config['Observer']
 
        self.scopeTxt.SetValue(scope)
        self.scopeportTxt.SetValue(scopeport)
        self.savefolderTxt.SetValue(savefolder)
        self.instportTxt.SetValue(instport)
        self.pixelscalexTxt.SetValue(pixelscalex)
        self.pixelscaleyTxt.SetValue(pixelscaley)
        self.observerTxt.SetValue(observer)
 
    #----------------------------------------------------------------------
    def editPreferences(self, event):
        """Allow a user to edit the preferences"""
        for widget in self.widgets:
            widget.Enable()
            
    #----------------------------------------------------------------------
    def editAdvPreferences(self, event):
        """Allow an admin to edit the preferences"""
        for widget in self.advwidgets:
            widget.Enable()        
        
    #----------------------------------------------------------------------
    def savePreferences(self, event):
        """
        Save the preferences
        """
        config = prefcontrol.getConfig()
 
        config['scope server'] = str(self.scopeTxt.GetValue())
        config['scope port'] = self.scopeportTxt.GetValue()
        config['savefolder'] = str(self.savefolderTxt.GetValue())
        config['instrument port'] = self.instportTxt.GetValue()
        config['pixel scale x'] = self.pixelscalexTxt.GetValue()
        config['pixel scale y'] = self.pixelscaleyTxt.GetValue()
        config['Observer'] = self.observerTxt.GetValue()
                
        config.write()

        for widget in self.advwidgets:
            widget.Disable() 
 
        dlg = wx.MessageDialog(self, "Preferences Saved!", 'Information',  
                               wx.OK|wx.ICON_INFORMATION)
        dlg.ShowModal()        
        
class PageFive(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super(PageFive, self).__init__(parent)
        
        # Attributes
        self.logTxt = wx.StaticText(self, wx.ID_ANY, "Instrument Log:")
        self.log = wx.TextCtrl(self, -1, size=(-1,130), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.log.SetBackgroundColour('#B0D6B0')
        self.obs_logTxt = wx.StaticText(self, wx.ID_ANY, "Observing Comments:")
        self.obs_log = wx.TextCtrl(self, -1, size=(-1,75), style=wx.TE_MULTILINE)
        self.log_button = wx.Button(self, label="Log")
        
        self.guidelogTxt = wx.StaticText(self, wx.ID_ANY, "Guiding Log:")
        self.guidelog = wx.TextCtrl(self, -1, size=(-1,130), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.guidelog.SetBackgroundColour('#B0D6B0')
        # Layout       
        self.__DoLayout()

    def __DoLayout(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        instSizer = wx.FlexGridSizer(cols=1, hgap=5, vgap=5)
        instSizer.AddGrowableCol(0)
        
        guideSizer = wx.FlexGridSizer(cols=1, hgap=5, vgap=5)
        guideSizer.AddGrowableCol(0)
        
        instSizer.Add(self.logTxt, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        instSizer.Add(self.log, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        instSizer.Add(self.obs_logTxt, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        instSizer.Add(self.obs_log, 0, wx.EXPAND)
        instSizer.Add(self.log_button, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
                    
        guideSizer.Add(self.guidelogTxt, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        guideSizer.Add(self.guidelog, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)            
                        
        mainSizer.Add(instSizer, 0, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(guideSizer, 0, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(mainSizer)

    def open_log(self):
        logtime = time.strftime("%a%d%b%Y-%H:%M:%S", time.gmtime())
        loggerfile = settings.save_folder+logtime+".log"
        self.logfile = open(loggerfile, 'a')
        self.logfile.write('Starting up ' + logtime + '\n')
    
    def close_log(self):
        log.close()
        
    def on_log_button(self, event):
        localtime = time.asctime(time.gmtime())
        note = self.obs_log.GetValue()
        self.log.AppendText(str(datetime.utcnow()) + '\n        ' + note + '\n\n')
        self.write_log(str(datetime.utcnow()) + '  ' + note)
        wx.TextCtrl.Clear(self.obs_log)
        
    def log_evt(self, msg):
        self.log.AppendText(str(datetime.utcnow()) + '\n        ' + msg.data + '\n')
        self.write_log(str(datetime.utcnow()) + '  ' + msg.data)
        self.parent.SetStatusText(msg.data)
    
    
    def write_log(self, note):
        #insert newline every 80 characters
        nlnote = self.insert_newlines(note)
        self.logfile.write('\n' + nlnote + '\n')

    def insert_newlines(self, string):
        dedented_text = textwrap.dedent(string).strip()
        return textwrap.fill(dedented_text, initial_indent='', subsequent_indent='    ', width=80)

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
