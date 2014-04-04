import logging
from time import sleep
import wx

import instrument.actuators.newport as new
from   threadtools import run_async
from   instrument.component import InstrumentError

class KmirrorPanel(wx.Panel):
    """This panel shows information and controls relevant to the Kmirror.

    Current PA: Shows the PA of the Kmirror in degrees CW from 0.
        New PA: A new angle to move the Kmirror.
          Move: Tell the Kmirror to go to the New PA.
          
    """
    def __init__(self, parent, kmirror):
        super(KmirrorPanel, self).__init__(parent)

        self.parent  = parent
        self.kmirror = kmirror

        #global k = None
        self.k_power = False        
        self.trackstatus = False
        self.jog_state = False
        self.vel = 0.0
        
        #GUI Components
        ################################################################
        self.curr_pa_text = wx.StaticText(self, label="Current PA:")
        self.curr_pa      = wx.StaticText(self, label="...")

        self.new_pa_text  = wx.StaticText(self, label="New PA:")
        self.new_pa       = wx.TextCtrl(self, size=(62,-1))
        self.set_button   = wx.Button(self,  size=(62,-1), label="Set")

        self.step_p    = wx.Button(self, size=(30,-1), label="+")
        self.step_m    = wx.Button(self, size=(30,-1), label="-")
        self.step_txt  = wx.StaticText(self, label="Step Size:")
        self.step_size = wx.SpinCtrl(self, pos=(0.1, 5), size=(62, -1), 
                                     min=1, max=5)

        self.track_button = wx.ToggleButton(self,  size=(62,-1), 
                                            label="Start Tracking")

        self.home_button = wx.Button(self, size=(62,-1), label="Home")

        self.mode_txt = wx.StaticText(self, label="Mode:")
        self.mode     = wx.ComboBox(
            self, -1, size=(126,-1), 
            choices=("Position Angle", "Vertical Angle", "Stationary"), 
            style=wx.CB_READONLY)

        self.t_angle_text  = wx.StaticText(self, label="T-Angle:")
        self.t_angle       = wx.TextCtrl(self, size=(62,-1))

                        
        # Layout
        ################################################################
        self.__DoLayout()
      
        # Event handlers
        ################################################################
        self.step_p.Bind(wx.EVT_BUTTON, self.step_pos)
        self.step_m.Bind(wx.EVT_BUTTON, self.step_neg)
        self.track_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_track)
        self.set_button.Bind(wx.EVT_BUTTON, self.on_set)
        self.Bind(wx.EVT_BUTTON, self.on_home, self.home_button)
            
        if self.kmirror is not None:
            # Set up a timer to update the current position angle
            TIMER_ID = 100 # Random number; it doesn't matter
            self.timer = wx.Timer(self, TIMER_ID)
            self.timer.Start(2000) # poll every 5 seconds
            wx.EVT_TIMER(self, TIMER_ID, self.on_timer)
        else:
            self.Enable(False)

        
    def __DoLayout(self):
        sbox = wx.StaticBox(self, label="Kmirror")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        #Add controls to gridbag
        ################################################################
        sizer.Add(self.curr_pa_text, pos=(0,0), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.curr_pa, pos=(0,1), flag=wx.ALIGN_LEFT)

        sizer.Add(self.new_pa_text,  pos=(1,0), 
                  flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.new_pa,  pos=(1,1), 
                  flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.set_button,  pos=(1,2), span=(1,2), 
                  flag=wx.ALIGN_LEFT)
        
        sizer.Add(self.step_m, pos=(2,2), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.step_p, pos=(2,3), flag=wx.ALIGN_LEFT)
        sizer.Add(self.step_txt, pos=(2,0), 
                  flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.step_size, pos=(2,1), 
                  flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.track_button,  pos=(3,0), span=(1,2), 
                  flag=wx.EXPAND)

        sizer.Add(self.home_button,  pos=(3,2), span=(1,2), 
                  flag=wx.ALIGN_LEFT)
        
        sizer.Add(self.mode_txt,  pos=(4,0), 
                  flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.mode, pos=(4,1), span=(1,3), flag=wx.ALIGN_LEFT)

        sizer.Add(self.t_angle_text, pos=(5,0), 
                  flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.t_angle, pos=(5,1), span=(1,4), flag=wx.ALIGN_LEFT)


        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(200, -1))
        boxSizer.Add(
            sizer, 
            flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        
    @run_async(daemon=True)
    def on_set(self, event):
        wx.CallAfter(self.Enable, False)
        try:
            pa = float(self.new_pa.GetValue())
            assert -170 <= pa <=170
            self.kmirror.move(pa)
        except InstrumentError:
            pass
        except ValueError:
            wx.CallAfter(wx.MessageBox,'Please select a valid number!', 
                         'INVALID Position Angle!', wx.OK | wx.ICON_ERROR)
        except AssertionError:
            wx.CallAfter(wx.MessageBox,'Please select a valid number!'
                         ' Valid range is -170 to 170', 
                         'INVALID Position Angle', 
                         wx.OK | wx.ICON_ERROR)
            
        wx.CallAfter(self.Enable, True)

    @run_async(daemon=True)
    def on_track(self, event):
        wx.CallAfter(self.Enable, False)
        children = self.GetChildren()
        if self.track_button.GetValue():
            wx.CallAfter(self.track_button.SetLabel, "Stop Tracking")
            wx.CallAfter(self.track_button.SetForegroundColour, (34,139,34))
            for child in children:
                if child != self.track_button: wx.CallAfter(child.Enable, False)
#            self.start_tracking()
        else:
            wx.CallAfter(self.track_button.SetLabel, "Start Tracking")
            wx.CallAfter(self.track_button.SetForegroundColour,(0,0,0))
            wx.CallAfter(self.Enable, True)
            for child in children:
                if child != self.track_button: wx.CallAfter(child.Enable, True)
#            self.stop_tracking()
        wx.CallAfter(self.Enable, True)


    def on_timer(self, event):
        try:
            pa = self.kmirror.positionAngle
            wx.CallAfter(self.curr_pa.SetLabel, u'%.3f \N{DEGREE SIGN}' % pa)
        except ValueError:
            pass
        
    @run_async(daemon=True)
    def step_pos(self, event):
        wx.CallAfter(self.Enable, False)
        try:
            step = self.step_size.GetValue()
            self.kmirror.step(step)
        except InstrumentError:
            pass
        wx.CallAfter(self.Enable, True)

    @run_async(daemon=True)
    def step_neg(self, event):
        wx.CallAfter(self.Enable, False)
        try:
            step = -1 * self.step_size.GetValue()
            self.kmirror.step(step)
        except InstrumentError:
            pass
        wx.CallAfter(self.Enable, True)

    @run_async(daemon=True)
    def on_home(self, event):
        wx.CallAfter(self.Enable, False)
        try:
            self.kmirror.home()
        except InstrumentError:
            pass
        wx.CallAfter(self.Enable, True)
