"""
Live update plotting of temps with matplot lib from code by Eli Bendersky
http://eli.thegreenplace.net/2008/08/01/matplotlib-with-wxpython-guis/
"""

#DEBUG = True

import os, sys
import random
import time
from datetime import datetime
import pprint
import cStringIO
import wx
#custom settings for GUI
import nessi_settings as settings
from wx.lib.stattext import GenStaticText
import threading
import numpy as np
import pylab
import ephem
import math
import subprocess
#for comminicating between panels
from wx.lib.pubsub import Publisher as pub

# Set the system path to the root directory of the Nessi set of libraries so we 
# can import our library modules in a consistent manner.
sys.path[0] = os.path.split(os.path.abspath(sys.path[0]))[0]
#import all of the control libraries
import libnessi.threadtools as threadtools #module from wxPython Cookbook by Cody Precord

#image manipulation
import Image
import backend.pic as pic
random.seed()

DEBUG = False
framecolor = wx.Color(175,175,175)
panelcolor = wx.Color(175,175,175)
sboxlabel  = wx.Color(34,139,34)
textcolor  = wx.Color(217,198,176)
################################################################################
#                           Panels for the GUI                                 #
################################################################################

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
        sbox.SetForegroundColour(sboxlabel)
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
        self.SetBackgroundColour(panelcolor)
        

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

class TelescopePanel(wx.Panel):
    """This panel shows information and controls relevant to the Telescope.
    """
    def __init__(self, parent, *args, **kwargs):
        super(TelescopePanel, self).__init__(parent)

        self.parent = parent

        # Attributes 
        self.curr_ra_text = wx.StaticText(self, label="RA:")
        self.curr_ra = wx.StaticText(self, label="Checking...")
        self.curr_dec_text = wx.StaticText(self, label="Dec:")
        self.curr_dec = wx.StaticText(self, label="Checking...")
        self.curr_alt_text = wx.StaticText(self, label="Alt:")
        self.curr_alt = wx.StaticText(self, label="Checking...")
        self.curr_az_text = wx.StaticText(self, label="Az:")
        self.curr_az = wx.StaticText(self, label="Checking...")
        self.curr_am_text = wx.StaticText(self, label="Air Mass:")
        self.curr_am = wx.StaticText(self, label="Checking...")
        self.curr_focus_text = wx.StaticText(self, label="Focus Position:")
        self.curr_focus = wx.StaticText(self, label="Checking...")


        # Layout
        self.__DoLayout()
        
        # Event Handlers
        
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
        sbox = wx.StaticBox(self, label="Telescope")
        sbox.SetForegroundColour(sboxlabel)
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        # Add controls to gridbag
        sizer.Add(self.curr_ra_text, pos=(0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_ra, pos=(0,1), flag=wx.ALIGN_LEFT)
        sizer.Add(self.curr_dec_text, pos=(1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_dec, pos=(1,1), flag=wx.ALIGN_LEFT)

        sizer.Add(wx.StaticLine(self), pos=(2,0), span=(1,2), flag=wx.EXPAND|wx.BOTTOM)

        sizer.Add(self.curr_alt_text, pos=(3,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_alt, pos=(3,1), flag=wx.ALIGN_LEFT)
        sizer.Add(self.curr_az_text, pos=(4,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_az, pos=(4,1), flag=wx.ALIGN_LEFT)
        
        sizer.Add(wx.StaticLine(self), pos=(5,0), span=(1,2), flag=wx.EXPAND|wx.BOTTOM)
        
        sizer.Add(self.curr_am_text, pos=(6,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_am, pos=(6,1), flag=wx.ALIGN_LEFT)
        sizer.Add(self.curr_focus_text, pos=(7,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_focus, pos=(7,1), flag=wx.ALIGN_LEFT)
        
        sizer.Add(wx.StaticLine(self), pos=(8,0), span=(1,2), flag=wx.EXPAND|wx.BOTTOM)
        
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(190, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        self.SetBackgroundColour(panelcolor)

        # Set up a timer to update the current position angle
        TIMER_ID = 200 # Random number; it doesn't matter
        self.timer = wx.Timer(self, TIMER_ID)
        self.timer.Start(500) # poll every 5 seconds
        wx.EVT_TIMER(self, TIMER_ID, self.on_timer)

        
    def on_timer(self, event):
        #can get this from telescope, but this will do for now, uses the sun as 
        #a test object to follow.
        mro = ephem.Observer()
        mro.elevation = 3233
        mro.long, mro.lat = '-107.189361', '33.984861'
        sun = ephem.Sun()
        sun.compute(mro)
        ra = sun.ra
        dec = sun.dec
        alt = sun.alt
        az = sun.az
        h = math.degrees(alt)
        am = round((1/math.sin(math.radians(h+244/(165+47*h**1.1)))), 4)
        self.curr_ra.SetLabel(str(ra))
        self.curr_dec.SetLabel(str(dec))
        self.curr_alt.SetLabel(str(alt))
        self.curr_az.SetLabel(str(az))
        self.curr_am.SetLabel(str(am))
        self.curr_focus.SetLabel(str(random.randint(0,800)))

class GuidePanel(wx.Panel):
    """This panel shows the images captured by the guide camera.
    """
    def __init__(self, parent, *args, **kwargs):
        super(GuidePanel, self).__init__(parent)
 
        self.parent = parent
        
        # Attributes
        
        #get image
        self.rawimage = pic.getimg('sdss.fits')
        #convert to wxImage
        guideimg = pic.PilImageToWxImage(self.rawimage)
        
        self.sBmp = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(guideimg))
        self.calibrate = wx.Button(self, size=(70,-1), label="Calibrate")
        self.guide = wx.ToggleButton(self, 1, size=(50,-1), label="Guide")
        self.log_onoff = wx.CheckBox(self, -1, 'Guiding Log On', (10,10))
        self.noise_onoff = wx.CheckBox(self, -1, 'Noise Reduction', (10,10))
        self.exposure = wx.TextCtrl(self, -1, '', size=(50,-1), style=wx.TE_NO_VSCROLL)
        self.exp_text = wx.StaticText(self, -1, label="Exposure \n(ms):")
        self.curr_exp = wx.StaticText(self, -1, label="xxxx ms")
        self.curr_exp_text = wx.StaticText(self, -1, label="Current:")
        self.set_exp = wx.Button(self, size=(35,-1), label="Set")
        
        self.contrast = wx.StaticText(self, label="Contrast")
        self.contrast_sld = wx.Slider(self, -1, 10, 0, 20, wx.DefaultPosition, (150, 20), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL)
        self.contrast_reset = wx.Button(self, size=(50,20), label="Reset")
        
        self.brightness = wx.StaticText(self, label="Brightness")
        self.brightness_sld = wx.Slider(self, -1, 10, 0, 20, wx.DefaultPosition, (150, 20), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL)
        self.brightness_reset = wx.Button(self, size=(50,20), label="Reset")
        
        self.guide_state = self.guide.GetValue()
         
        # Layout
        self.__DoLayout()
        
        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.Set_Exp, self.set_exp)
        self.Bind(wx.EVT_BUTTON, self.ResetContrast, self.contrast_reset)
        self.Bind(wx.EVT_BUTTON, self.ResetBrightness, self.brightness_reset)
        
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnGuide, id=1)
        
        self.Bind(wx.EVT_SLIDER, self.AdjContBri, self.contrast_sld)
        self.Bind(wx.EVT_SLIDER, self.AdjContBri, self.brightness_sld)
        
    def __DoLayout(self):
        sbox = wx.StaticBox(self, label="Guide Camera")
        sbox.SetForegroundColour(sboxlabel)
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        # Add controls to gridbag
        sizer.Add(self.sBmp, pos=(0,0), span=(1,8), flag=wx.ALIGN_CENTER)
        
        sizer.Add(self.calibrate, pos=(1,0), span=(2,1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.guide, pos=(1,1), span=(2,1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.log_onoff, pos=(1,2), span=(1,2), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.noise_onoff, pos=(2,2), span=(1,2), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        sizer.Add(self.exp_text, pos=(3,0), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.exposure, pos=(3,1), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)        
        sizer.Add(self.set_exp, pos=(3,2), span=(1,1), flag=wx.ALIGN_CENTER)
        sizer.Add(self.curr_exp_text, pos=(4,0), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_exp, pos=(4,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)         
        
        sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), pos=(1,4), span=(5,1), flag=wx.EXPAND)
        
        sizer.Add(self.contrast, pos=(1,5), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.contrast_sld, pos=(1,6), span=(1,1), flag=wx.ALIGN_CENTER)
        sizer.Add(self.contrast_reset, pos=(1,7), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.brightness, pos=(2,5), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.brightness_sld, pos=(2,6), span=(1,1), flag=wx.ALIGN_CENTER)
        sizer.Add(self.brightness_reset, pos=(2,7), flag=wx.ALIGN_CENTER_VERTICAL)
                        
        # Add the grid bag to the static box and make everything fit
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        self.SetBackgroundColour(panelcolor)

    def Set_Exp(self, event):
        expose = self.exposure.GetValue()
        self.curr_exp.SetLabel(str(expose))
        
    def OnGuide(self, event):
        if self.guide.GetValue():
            pub.sendMessage("LOG EVENT", 'guiding')
        
        else:
            pub.sendMessage("LOG EVENT", 'stopped guiding')
    
    def AdjContBri(self, event):
        curcon = self.contrast_sld.GetValue()*0.1
        curbri = self.brightness_sld.GetValue()*0.1
        adjusted = pic.pic_cont_bri(self.rawimage, curcon, curbri)
        adjusted = pic.PilImageToWxImage(adjusted)
        self.sBmp.SetBitmap(wx.BitmapFromImage(adjusted))
   
    def ResetContrast(self, event):
        self.contrast_sld.SetValue(10)
        self.AdjContBri(event)
        
    def ResetBrightness(self, event):    
        self.brightness_sld.SetValue(10)
        self.AdjContBri(event)


class TempPanel(wx.Panel):
    """This panel shows information on the Lakeshore temperature sensors.
    """
    def __init__(self, parent, *args, **kwargs):
        super(TempPanel, self).__init__(parent)

        self.parent = parent
        self.done = True

        # Attributes 
        self.curr_ts1_text = wx.StaticText(self, label="IR FPA:")
        self.curr_ts1 = wx.StaticText(self, label="... ")
        self.curr_ts2_text = wx.StaticText(self, label="Guide Camera:")
        self.curr_ts2 = wx.StaticText(self, label="... ")
        self.curr_ts3_text = wx.StaticText(self, label="Dewar Top:")
        self.curr_ts3 = wx.StaticText(self, label="... ")
        self.curr_ts4_text = wx.StaticText(self, label="Dewar Bottom:")
        self.curr_ts4 = wx.StaticText(self, label="... ")
        self.curr_ts5_text = wx.StaticText(self, label="Ambient:")
        self.curr_ts5 = wx.StaticText(self, label="... ")
        
        # Layout
        self.__DoLayout()
        
        # Event Handlers
        
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
        sbox = wx.StaticBox(self, label="Temperature")
        sbox.SetForegroundColour(sboxlabel)
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        # Add controls to gridbag
        sizer.Add(self.curr_ts1_text, pos=(0,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_ts1, pos=(0,1), flag=wx.ALIGN_LEFT)

        sizer.Add(wx.StaticLine(self), pos=(1,0), span=(1,2), flag=wx.EXPAND|wx.BOTTOM)

        sizer.Add(self.curr_ts2_text, pos=(2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_ts2, pos=(2,1), flag=wx.ALIGN_LEFT)
        
        sizer.Add(wx.StaticLine(self), pos=(3,0), span=(1,2), flag=wx.EXPAND|wx.BOTTOM)

        sizer.Add(self.curr_ts3_text, pos=(4,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_ts3, pos=(4,1), flag=wx.ALIGN_LEFT)
        
        sizer.Add(wx.StaticLine(self), pos=(5,0), span=(1,2), flag=wx.EXPAND|wx.BOTTOM)

        sizer.Add(self.curr_ts4_text, pos=(6,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_ts4, pos=(6,1), flag=wx.ALIGN_LEFT)
        
        sizer.Add(wx.StaticLine(self), pos=(7,0), span=(1,2), flag=wx.EXPAND|wx.BOTTOM)

        sizer.Add(self.curr_ts5_text, pos=(8,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_ts5, pos=(8,1), flag=wx.ALIGN_LEFT)

        sizer.Add(wx.StaticLine(self), pos=(9,0), span=(1,2), flag=wx.EXPAND|wx.BOTTOM)

        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(140, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        self.SetBackgroundColour(panelcolor)

        # Set up a timer to update the current position angle
        TIMER_ID = 200 # Random number; it doesn't matter
        self.timer = wx.Timer(self, TIMER_ID)
        self.timer.Start(20000) # poll every 20 seconds
        wx.EVT_TIMER(self, TIMER_ID, self.on_timer)

    def on_timer(self, event):
        if self.done:
            self.thread = Temps(self)
            self.thread.daemon=True
            self.thread.start()
        else:
            pass
           
    @threadtools.callafter
    def set_temp_text(self, temps):
        #format temp display
        temp1 = temps[0] + u'\N{DEGREE SIGN}' + 'C' #top
        temp2 = temps[1] + u'\N{DEGREE SIGN}' + 'C' #proximal
        temp3 = temps[2] + u'\N{DEGREE SIGN}' + 'C' #distal
        temp4 = temps[3] + u'\N{DEGREE SIGN}' + 'C' #under
        temp5 = temps[4] + u'\N{DEGREE SIGN}' + 'C' #external
        
        #only try and write new temps if we have actual number values for temps
        if temp1[:-2] != '..':
            self.curr_ts1.SetLabel(temp1)
            self.curr_ts2.SetLabel(temp2)
            self.curr_ts3.SetLabel(temp3)
            self.curr_ts4.SetLabel(temp4)
            self.curr_ts5.SetLabel(temp5)
           
            #raise error state if temp diff between one of the sensors
            #and the external temp is greater than 5degC
            if float(temp1[:-2]) - float(temp5[:-2]) >= 1.0:
                self.curr_ts1.SetForegroundColour((255,0,0))
                temp1 = temp1 + '  ' + u'\u2622' + '+'
                self.curr_ts1.SetLabel(temp1)
            else:
                self.curr_ts1.SetForegroundColour((34,139,34))

            if float(temp2[:-2]) - float(temp5[:-2]) >= 1.0:
                self.curr_ts2.SetForegroundColour((255,0,0))
                temp2 = temp2 + '  ' + u'\u2622' + '+'
                self.curr_ts2.SetLabel(temp2)
            else:
                self.curr_ts2.SetForegroundColour((34,139,34))
            
            if float(temp3[:-2]) - float(temp5[:-2]) >= 1.0:
                self.curr_ts3.SetForegroundColour((255,0,0))
                temp3 = temp3 + '  ' + u'\u2622' + '+'
                self.curr_ts3.SetLabel(temp3)
            else:
                self.curr_ts3.SetForegroundColour((34,139,34))
            
            if float(temp4[:-2]) - float(temp5[:-2]) >= 1.0:
                self.curr_ts4.SetForegroundColour((255,0,0))
                temp4 = temp4 + '  ' + u'\u2622' + '+'
                self.curr_ts4.SetLabel(temp4)
            else:
                self.curr_ts4.SetForegroundColour((34,139,34))
        else:
            pass
  
class GuideInfoPanel(wx.Panel):
    """This panel shows information on the guide camera system."""
    def __init__(self, parent, *args, **kwargs):
        super(GuideInfoPanel, self).__init__(parent)

        self.parent = parent
        
        # Attributes 
        self.curr_scale_text = wx.StaticText(self, label="arcsec/px:")
        self.curr_scale = wx.StaticText(self, label="Checking...")
        self.curr_moverate_text = wx.StaticText(self, label="Move Rate (arcsec/s):")
        self.curr_moverate = wx.StaticText(self, label="Checking...")
        self.curr_damping_text = wx.StaticText(self, label="Correction Damping:")
        self.curr_damping = wx.StaticText(self, label="Checking...")

        self.guide_hist = wx.StaticBitmap(self)
        self.guide_hist.SetFocus()
        self.guide_hist.SetBitmap(wx.Bitmap('guide_err.png'))
        # Layout
        self.__DoLayout()
        
        # Event Handlers
        
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
        sbox.SetForegroundColour(sboxlabel)
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        # Add controls to gridbag
        sizer.Add(self.curr_scale_text, pos=(0,0), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_scale, pos=(0,1), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_moverate_text, pos=(1,0), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_moverate, pos=(1,1), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_damping_text, pos=(2,0), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_damping, pos=(2,1), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.guide_hist, pos=(3,0), span=(1,2), flag=wx.ALIGN_CENTER_HORIZONTAL)
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(350, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        self.SetBackgroundColour(panelcolor)
        
class GrismPanel(wx.Panel):
    """This panel controls the Grism wheel"""
    def __init__(self, parent, *args, **kwargs):
        super(GrismPanel, self).__init__(parent) 
        
        self.parent = parent

        # Attributes        
        self.grism = settings.grism
    
        self.curr_filter_text = wx.StaticText(self, label="Current Grism:")
        self.curr_filter = wx.StaticText(self, label="Checking...")
        self.select_button = wx.Button(self, label="Select")
        self.filter_choice = wx.ComboBox(self, -1, size=(100,-1), choices=self.grism, style=wx.CB_READONLY)
    
        # Layout
        self.__DoLayout()
        # Event handlers
        self.Bind(wx.EVT_COMBOBOX, self.on_select, self.filter_choice)
        self.Bind(wx.EVT_BUTTON, self.move_filter, self.select_button)
        
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
        sbox.SetForegroundColour(sboxlabel)
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.curr_filter_text,  pos=(0,0), flag=wx.ALIGN_LEFT)
        sizer.Add(self.curr_filter,  pos=(0,1), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.filter_choice, pos=(1,0), flag=wx.ALIGN_CENTER)
        sizer.Add(self.select_button, pos=(1,1), flag=wx.ALIGN_CENTER)
    
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(200, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        self.SetBackgroundColour(panelcolor)

    def on_select(self, event):
        try:
            selected = event.GetSelection()
            pub.sendMessage("LOG EVENT", "Chosen guide filter is..." + str(self.grism[selected]))
            return selected
        except ValueError:
            pass

    def move_filter(self, event):
        try:
            pub.sendMessage("LOG EVENT", "Moving to guide filter...")
            selected = self.filter_choice.GetSelection()
            self.curr_filter.SetLabel(self.grism[selected])
        except ValueError:
            pass

class MaskPanel(wx.Panel):
    """This panel controls the Apogee filter wheel for the guide camera"""
    def __init__(self, parent, *args, **kwargs):
        super(MaskPanel, self).__init__(parent) 
        
        self.parent = parent

        # Attributes        
        self.masks = settings.mask 
        
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
        
        sbox = wx.StaticBox(self, label="Mask")
        sbox.SetForegroundColour(sboxlabel)
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
        self.SetBackgroundColour(panelcolor)

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

class FWPanel(wx.Panel):
    """This panel controls the FLI filter wheel """
    def __init__(self, parent, *args, **kwargs):
        super(FWPanel, self).__init__(parent) 
        
        self.parent = parent

        # Attributes
        self.filters = settings.fw
    
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
        sbox = wx.StaticBox(self, label="Filter")
        sbox.SetForegroundColour(sboxlabel)
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
        self.SetBackgroundColour(panelcolor)

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

class GuideFocusPanel(wx.Panel):
    """This panel shows information and controls relevant to the linear stage
    for focusing the FLI Guide camera.

    Current Position (mm): Shows the position of the stage in mm from 0.
        New Position: A new position to move the stage.
          Move: Tell the stage to go to the new position.
    """
    def __init__(self, parent, *args, **kwargs):
        super(GuideFocusPanel, self).__init__(parent)

        self.parent = parent
        #self.s = Stage()
        
        # Attributes
        self.curr_pos_text = wx.StaticText(self, label="Current Position (mm):")
        self.curr_pos = wx.StaticText(self, label="...")
        self.new_pos_text = wx.StaticText(self, label="New Position (0-100):")
        self.new_pos = wx.TextCtrl(self, size=(62,-1))
                
        self.home_button = wx.Button(self, size=(62,-1), label="Home")
        self.move_button = wx.Button(self, size=(62,-1), label="Move")
        self.stop_button = wx.Button(self, size=(62,-1), label="Stop")
        
        self.step_p = wx.Button(self, size=(30,-1), label="+")
        self.step_m = wx.Button(self, size=(30,-1), label="-")
        self.step_txt = wx.StaticText(self, label="Step Size:")
        self.step_size = wx.SpinCtrl(self, -1, '', (0.1, 5), (62, -1))
        self.step_size.SetRange(1, 5)
        self.step_size.SetValue(1)

        # Layout
        self.__DoLayout()
        
        # Event handlers
        self.Bind(wx.EVT_BUTTON, self.on_move, self.move_button)
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.stop_button)
        self.Bind(wx.EVT_BUTTON, self.on_home, self.home_button)

    def __DoLayout(self):
        ## Layout for this panel:
        ##
        ##    0               1
        ##   +---------------+---------------+
        ## 0 | curr_pos_text | self.curr_pos |
        ##   +---------------+---------------+
        ## 1 | new_pos_text  | self.new_pos  |
        ##   +---------------+---------------+
        ## 2 | move_button   | stop_button   |
        ##   +---------------+---------------+
        ## 3 | home_button   |               |
        ##   +---------------+---------------+
        sbox = wx.StaticBox(self, label="Guide Camera Focus Stage")
        sbox.SetForegroundColour(sboxlabel)
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.curr_pos_text, pos=(0,0), span=(1,2), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.curr_pos, pos=(0,2), span=(1,2), flag=wx.ALIGN_LEFT)

        sizer.Add(self.new_pos_text,  pos=(1,0), span=(1,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.new_pos,  pos=(1,2), span=(1,2), flag=wx.ALIGN_LEFT)

        sizer.Add(self.step_m, pos=(2,2), flag=wx.ALIGN_LEFT)
        sizer.Add(self.step_p, pos=(2,3), flag=wx.ALIGN_LEFT)
        
        sizer.Add(self.step_txt, pos=(2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.step_size, pos=(2,1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.move_button,  pos=(3,0), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.stop_button,  pos=(3,1), flag=wx.ALIGN_LEFT)

        sizer.Add(self.home_button,  pos=(3,2), span=(1,2), flag=wx.ALIGN_LEFT)
                
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(200, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        self.SetBackgroundColour(panelcolor)
        
        
        # Set up a timer to update the current position angle
        TIMER_ID = 100 # Random number; it doesn't matter
        self.timer = wx.Timer(self, TIMER_ID)
        self.timer.Start(2000) # poll every 2 seconds
        wx.EVT_TIMER(self, TIMER_ID, self.on_timer)

    def on_move(self, event):
        try:
            pos = float(self.new_pos.GetValue())
            pub.sendMessage("LOG EVENT", "Stage move to %f" % pos)
            #self.s.set_pos(pos)
            
        except ValueError:
            pass # TODO: Error Message

    def on_stop(self, event):
        try:
            #self.s.stop()
            pub.sendMessage("LOG EVENT", "Stage Stopped...")
        except ValueError:
            pass
        
    def on_home(self, event):
        #self.s.home()
        pass
    
    def on_timer(self, event):
        #pos = self.s.get_pos()
        pos = random.randint(0,10)
        self.curr_pos.SetLabel(str(pos))

class ReImageFocusPanel(wx.Panel):
    """This panel shows information and controls relevant to the linear stage
    for focusing the re-imaging lens.

    Current Position (mm): Shows the position of the stage in mm from 0.
        New Position: A new position to move the stage.
          Move: Tell the stage to go to the new position.
    """
    def __init__(self, parent, *args, **kwargs):
        super(ReImageFocusPanel, self).__init__(parent)

        self.parent = parent
        #self.s = Stage()
        
        # Attributes
        self.curr_pos_text = wx.StaticText(self, label="Current Position (mm):")
        self.curr_pos = wx.StaticText(self, label="...")
        self.new_pos_text = wx.StaticText(self, label="New Position (0-100):")
        self.new_pos = wx.TextCtrl(self, size=(62,-1))
                
        self.home_button = wx.Button(self, size=(62,-1), label="Home")
        self.move_button = wx.Button(self, size=(62,-1), label="Move")
        self.stop_button = wx.Button(self, size=(62,-1), label="Stop")

        self.step_p = wx.Button(self, size=(30,-1), label="+")
        self.step_m = wx.Button(self, size=(30,-1), label="-")
        self.step_txt = wx.StaticText(self, label="Step Size:")
        self.step_size = wx.SpinCtrl(self, -1, '', (0.1, 5), (62, -1))
        self.step_size.SetRange(1, 5)
        self.step_size.SetValue(1)
        
        # Layout
        self.__DoLayout()
        
        # Event handlers
        self.Bind(wx.EVT_BUTTON, self.on_move, self.move_button)
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.stop_button)
        self.Bind(wx.EVT_BUTTON, self.on_home, self.home_button)

    def __DoLayout(self):
        ## Layout for this panel:
        ##
        ##    0               1
        ##   +---------------+---------------+
        ## 0 | curr_pos_text | self.curr_pos |
        ##   +---------------+---------------+
        ## 1 | new_pos_text  | self.new_pos  |
        ##   +---------------+---------------+
        ## 2 | move_button   | stop_button   |
        ##   +---------------+---------------+
        ## 3 | home_button   |               |
        ##   +---------------+---------------+
        sbox = wx.StaticBox(self, label="Re-Imaging Lens Focus Stage")
        sbox.SetForegroundColour(sboxlabel)
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.curr_pos_text, pos=(0,0), span=(1,2), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.curr_pos, pos=(0,2), span=(1,2), flag=wx.ALIGN_LEFT)

        sizer.Add(self.new_pos_text,  pos=(1,0), span=(1,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.new_pos,  pos=(1,2), span=(1,2), flag=wx.ALIGN_LEFT)

        sizer.Add(self.step_m, pos=(2,2), flag=wx.ALIGN_LEFT)
        sizer.Add(self.step_p, pos=(2,3), flag=wx.ALIGN_LEFT)
        
        sizer.Add(self.step_txt, pos=(2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.step_size, pos=(2,1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.move_button,  pos=(3,0), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.stop_button,  pos=(3,1), flag=wx.ALIGN_LEFT)

        sizer.Add(self.home_button,  pos=(3,2), span=(1,2), flag=wx.ALIGN_LEFT)
        
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(160, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        self.SetBackgroundColour(panelcolor)


        # Set up a timer to update the current position angle
        TIMER_ID = 100 # Random number; it doesn't matter
        self.timer = wx.Timer(self, TIMER_ID)
        self.timer.Start(2000) # poll every 2 seconds
        wx.EVT_TIMER(self, TIMER_ID, self.on_timer)

    def on_move(self, event):
        try:
            #pos = float(self.new_pos.GetValue())
            pub.sendMessage("LOG EVENT", "Stage move to %f" % pos)
            self.s.set_pos(pos)
            
        except ValueError:
            pass # TODO: Error Message

    def on_stop(self, event):
        try:
            #self.s.stop()
            pub.sendMessage("LOG EVENT", "Stage Stopped...")
        except ValueError:
            pass
        
    def on_home(self, event):
        #self.s.home()
        pass
    
    def on_timer(self, event):
        #pos = self.s.get_pos()
        pos = random.randint(0,10)
        self.curr_pos.SetLabel(str(pos))

class EnvironPanel(wx.Panel):
    """This panel controls the environmental cover"""
    def __init__(self, parent, *args, **kwargs):
        super(EnvironPanel, self).__init__(parent) 
        
        self.parent = parent

        # Attributes        
        self.open_close_button = wx.ToggleButton(self, 1, label="Open")
        self.status_text       = wx.StaticText(self, label="The cover is currently:")
        self.status            = wx.StaticText(self, label="Closed " + u'\u2612')
        self.status.SetForegroundColour((255,0,0))
        self.open_close_button.SetForegroundColour((34,139,34))
        
        # Layout
        self.__DoLayout()
        
        # Event handlers
        self.Bind(wx.EVT_TOGGLEBUTTON, self.operate, self.open_close_button)
        
    def __DoLayout(self):
        ## Layout for this panel:
        ##
        ##    0                      1
        ##   +--------------------+---------------------+
        ## 0 |  curr_mask_text   |   curr_mask          |
        ##   +-------------------+----------------------+
        ## 1 |   select_button   |    mask_choice       |
        ##   +-------------------+----------------------+
        
        sbox = wx.StaticBox(self, label="Environmental Cover")
        sbox.SetForegroundColour(sboxlabel)
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        # Add controls to gridbag
        sizer.Add(self.status_text, pos=(0,0), flag=wx.ALIGN_CENTER)
        sizer.Add(self.status, pos=(0,1), flag=wx.ALIGN_CENTER)
        sizer.Add(self.open_close_button, pos=(1,0), span=(1,2), flag=wx.ALIGN_CENTER)
    
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(190, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        self.SetBackgroundColour(panelcolor)

        
    def operate(self, event):
        if self.open_close_button.GetValue():
            pub.sendMessage("LOG EVENT", "The environmental cover is open.")
            self.open_close_button.SetLabel(" CLOSE ")
            self.open_close_button.SetForegroundColour((255,0,0))
            self.status.SetForegroundColour((34,139,34))
            self.status.SetLabel("Open " + u'\u2611')
        else:
            shut = self.on_shut()
            if shut == 5103:
                pub.sendMessage("LOG EVENT", "The environmental cover is closed.")
                self.open_close_button.SetLabel("OPEN")
                self.open_close_button.SetForegroundColour((34,139,34))
                self.status.SetForegroundColour((255,0,0))
                self.status.SetLabel("Closed " + u'\u2612')
            else:
                #set the toggle button state to keep pressed/not pressed consistent with labeling of button
                self.open_close_button.SetValue(True)
            
    def on_shut(self):
        """Check to see if the user really wants to close the environmental cover."""
        if self.open_close_button.GetValue():
            pass
        else:
            wx.Bell()
            env_alert = wx.MessageDialog(self, 'Are you sure you want to close the environmental cover?', style=wx.YES_NO|wx.CENTER|wx.ICON_EXCLAMATION)
            answer = env_alert.ShowModal()
            return answer
            
class LogPanel(wx.Panel):
    """This panel shows a running log of all commands and can be saved to record
    the observing session (with time stamps).
    """
    def __init__(self, parent, *args, **kwargs):
        super(LogPanel, self).__init__(parent)

        self.parent = parent
        
        # Attributes
        self.log = wx.TextCtrl(self, -1, size=(350,100), style=wx.TE_MULTILINE|wx.TE_READONLY)
        
        self.obs_log = wx.TextCtrl(self, -1, size=(288,80), style=wx.TE_MULTILINE)
        self.log_button = wx.Button(self, size=(60,-1), label="Log")
        self.saveas_button = wx.Button(self, size=(60,-1), label="Save As")
        
        # Layout
        self.__DoLayout()
        
        # Event handlers
        self.Bind(wx.EVT_BUTTON, self.on_log_button, self.log_button)
        
    def __DoLayout(self):
        ## Layout for this panel:
        ##
        ##    0               
        ##   +---------------+
        ## 0 |     Log       |
        ##   +---------------+
        ## 1 |    save       |
        ##   +---------------+
        sbox = wx.StaticBox(self, label="Instrument Log")
        sbox.SetForegroundColour(sboxlabel)
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.log, pos=(0,0), span=(1,2), flag=wx.ALIGN_CENTER)
        sizer.Add(self.obs_log, pos=(1,0), span=(2,1), flag=wx.ALIGN_LEFT)
        sizer.Add(self.log_button,  pos=(1,1), span=(1,1), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.saveas_button,  pos=(2,1), span=(1,1), flag=wx.ALIGN_RIGHT)
        
        self.log.SetBackgroundColour((202,225,255))
        # Add the grid bag to the static box and make everything fit
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        self.SetBackgroundColour(panelcolor)
        self.log.SetBackgroundColour(wx.Color(220,220,220))
        # Set up a timer to update the current position angle
        TIMER_ID = 100 # Random number; it doesn't matter
        self.timer = wx.Timer(self, TIMER_ID)
        self.timer.Start(2000) # poll every 20 seconds
        wx.EVT_TIMER(self, TIMER_ID, self.on_timer)
        
        #subscribe to messages
        pub.subscribe(self.log_evt)

    def on_timer(self, event):
        pass
        #localtime = time.asctime( time.localtime(time.time()))
        #self.log.AppendText(str(datetime.utcnow()) + '\n        this is a test\n')
        
    def on_log_button(self, event):
        localtime = time.asctime(time.gmtime())
        note = self.obs_log.GetValue()
        self.log.AppendText(str(datetime.utcnow()) + '\n        ' + note + '\n\n')
        wx.TextCtrl.Clear(self.obs_log)
        
    def log_evt(self, msg):
        self.log.AppendText(str(datetime.utcnow()) + '\n        ' + msg.data + '\n')
        self.parent.SetStatusText(msg.data)

class LogWriter:
    """This class will be used to write all actions of the gui/user to a log file
    it will create a new log file every time the gui is started.
    """
    def open_log(self):
        logfile = time.strftime("%a%d%b%Y-%H:%M:%S.log", time.gmtime())
        global log
        log = open(logfile, 'a')
        log.write('Starting up ' + logfile[:21])
    
    def write_log(self, message):
        log.write(message)
        
    def close_log(self):
        log.close()
    

################################################################################
#                           Main Frame and App                                 #
################################################################################

        
class MainFrame(wx.Frame):
    """Main Frame holding all of our Panels.  The structure is as follows:
       0                    1                    2                    3
    +--------------------+--------------------+--------------------+-----------+
  0 |  GuidecamPanel     |  PupilcamPanel     |  GuideFWPanel      |           |
    +--------------------+--------------------+--------------------+   Power   |
  1 |  GuideControlPanel |  TelescopePanel    |  MaskPanel         |           |
    +--------------------+--------------------+--------------------+ ----------|
  2 |  StatusUpdatePanel |  KmirrorPanel      |  FilterPanel       |           |
    +--------------------+--------------------+--------------------+  Temps    |
  3 |                    |                    |  LinearStagePanel  |           |
    +--------------------+--------------------+--------------------+-----------+    
    guide and pupil cam panels hold images from these cameras.

    KmirrorPanel holds info and controls for the Kmirror.

    TelescopePanel holds info and controls for the Telescope.
    """
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)

        # Attributes
        self.create_menus()
        self.CreateStatusBar()

        self.GuidePanel = GuidePanel(self)
        self.LogPanel = LogPanel(self)
        self.KmirrorPanel = KmirrorPanel(self)
        self.TelescopePanel = TelescopePanel(self)
        self.GrismPanel = GrismPanel(self)
        self.MaskPanel = MaskPanel(self)
        self.FWPanel = FWPanel(self)
        self.TempPanel = TempPanel(self)
        self.GuideFocusPanel = GuideFocusPanel(self)
        self.GuideInfoPanel = GuideInfoPanel(self)
        self.ReImageFocusPanel = ReImageFocusPanel(self)
        self.EnvironPanel = EnvironPanel(self)

        self.logo = wx.StaticBitmap(self)
        self.logo.SetFocus()
        self.logo.SetBitmap(wx.Bitmap('nessi-logo.png'))
        
        # Layout
        sizer = wx.GridBagSizer(vgap=5, hgap=5)
        #sizer.Add(self.logo,              pos=(0,0), span=(1,1), flag=wx.ALIGN_CENTER_HORIZONTAL)
        sizer.Add(self.GuidePanel,        pos=(0,2), span=(7,2), flag=wx.ALIGN_CENTER_HORIZONTAL)
        sizer.Add(self.GrismPanel,        pos=(0,4), span=(1,1), flag=wx.ALIGN_LEFT|wx.RIGHT, border=5)
        sizer.Add(self.MaskPanel,         pos=(1,4), span=(1,1), flag=wx.ALIGN_LEFT|wx.RIGHT, border=5)
        sizer.Add(self.FWPanel,           pos=(2,4), span=(1,1), flag=wx.ALIGN_LEFT|wx.RIGHT, border=5)
        sizer.Add(self.GuideFocusPanel,   pos=(3,4), span=(1,1), flag=wx.ALIGN_LEFT|wx.RIGHT, border=5)
        sizer.Add(self.ReImageFocusPanel, pos=(4,4), span=(1,1), flag=wx.ALIGN_LEFT|wx.RIGHT, border=5)
        sizer.Add(self.KmirrorPanel,      pos=(5,4), span=(2,1), flag=wx.ALIGN_LEFT|wx.RIGHT, border=5)
        
        sizer.Add(self.EnvironPanel,      pos=(0,1), span=(1,1), flag=wx.ALIGN_RIGHT|wx.LEFT, border=5)
        sizer.Add(self.TelescopePanel,    pos=(1,1), span=(2,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_TOP)
        sizer.Add(self.TempPanel,         pos=(1,0), span=(2,1), flag=wx.ALIGN_LEFT|wx.ALIGN_TOP|wx.LEFT, border=5)
        sizer.Add(self.GuideInfoPanel,    pos=(3,0), span=(3,2), flag=wx.ALIGN_RIGHT|wx.LEFT, border=5)
        
        sizer.Add(self.LogPanel,          pos=(6,0), span=(2,2), flag=wx.ALIGN_LEFT|wx.LEFT, border=5)
                
        # Add icon
        path = os.path.abspath("./nessi.png")
        icon = wx.Icon(path, wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)
        
        self.SetBackgroundColour(framecolor)
        self.SetSizerAndFit(sizer)
        self.CenterOnScreen()
        self.Show()
        #self.log = LogWriter()
        #self.log.open_log()

    def create_menus(self):
        menuBar = wx.MenuBar()

        # Attributes
        FileMenu = wx.Menu()
        about_item   = FileMenu.Append(wx.ID_ABOUT, text="&About NESSI Controller")
        open_item    = FileMenu.Append(wx.ID_OPEN, text="&Open Configuration...")
        save_as_item = FileMenu.Append(wx.ID_SAVEAS, text="&Save Configuration As...")
        prefs_item   = FileMenu.Append(wx.ID_PREFERENCES, text="&Preferences") 
        quit_item    = FileMenu.Append(wx.ID_EXIT, text="&Quit")
        
        # Event Handlers
        self.Bind(wx.EVT_MENU, self.OnAbout, about_item)
        self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
        
        menuBar.Append(FileMenu, "&File")
        self.SetMenuBar(menuBar)

    def OnQuit(self, event=None):
        #KmirrorPanel.k.__del__()
        #log.close_log()
        self.Close()
        
    def OnAbout(self, event=None):
        info = wx.AboutDialogInfo()
        info.SetName('NESSI Controller')
        info.SetVersion('0.1')
        info.SetDescription('NESSI Controller is an interface to the New Mexico Tech Extrasolar Spectroscopic Survey Instrument. Email lschmidt@nmt.edu with questions.')
        info.SetCopyright('(C) 2011 Luke Schmidt, NMT/MRO')

        wx.AboutBox(info)

class AmasingApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame(None, title = "NESSI Control panel")
        self.frame.Show()
        return True

if __name__ == '__main__':
    app = AmasingApp(False)
    app.MainLoop()
