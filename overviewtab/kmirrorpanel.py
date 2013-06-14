
import logging
from time import sleep
import wx

import actuators.newport as new
from threadtools import run_async

class KmirrorPanel(wx.Panel):
    """This panel shows information and controls relevant to the Kmirror.

    Current PA: Shows the PA of the Kmirror in degrees CW from 0.
        New PA: A new angle to move the Kmirror.
          Move: Tell the Kmirror to go to the New PA.
          
    """
    def __init__(self, parent, motor, controller, socket, *args, **kwargs):
        #wx.Panel.__init__(self, parent, *args, **kwargs)
        super(KmirrorPanel, self).__init__(parent)

        self.parent = parent
        self.controller = controller
        self.socket = socket
        self.motor = motor

        #global k = None
        self.k_power = False        
        self.trackstatus = False
        self.jog_state = False
        self.vel = 0.0
        new.NewportInitialize(self.controller, self.motor, self.socket[0], 0)
        
        # Attributes
        self.curr_pa_text = wx.StaticText(self, label="Current PA:")
        self.curr_pa = wx.StaticText(self, label="...")
        self.new_pa_text = wx.StaticText(self, label="New PA:")
        self.new_pa = wx.TextCtrl(self, size=(62,-1))

        self.step_p = wx.Button(self, size=(30,-1), label="+")
        self.step_m = wx.Button(self, size=(30,-1), label="-")
        self.track_button = wx.ToggleButton(self,  size=(62,-1), label="Start Tracking")
        self.set_button = wx.Button(self,  size=(62,-1), label="Set")
#        self.stop_button = wx.Button(self,  size=(62,-1), label="Stop")
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
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_track, self.track_button)
        self.Bind(wx.EVT_BUTTON, self.on_set, self.set_button)
#        self.Bind(wx.EVT_BUTTON, self.on_stop, self.stop_button)
        self.Bind(wx.EVT_BUTTON, self.on_home, self.home_button)

        
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

        sizer.Add(self.track_button,  pos=(3,0), span=(1,2), flag=wx.EXPAND)
#        sizer.Add(self.stop_button,  pos=(3,1), flag=wx.ALIGN_LEFT)
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

    @run_async
    def on_set(self, event):
        wx.CallAfter(self.Enable, False)
        try:
            pa = float(self.new_pa.GetValue())
            logging.info('Rotator: Move to %f' % (float(pa)) + u'\N{DEGREE SIGN}')
            new.NewportKmirrorMove(self.controller, self.socket[0], self.motor, self.jog_state, pa)
            logging.info('Rotator: Is at %f' % (float(pa)) + u'\N{DEGREE SIGN}')
            
        except ValueError:
            pass
        wx.CallAfter(self.Enable, True)
        
    @run_async
    def on_track(self, event):
        children = self.GetChildren()
        if self.track_button.GetValue():
            wx.CallAfter(self.track_button.SetLabel, "Stop Tracking")
            wx.CallAfter(self.track_button.SetForegroundColour, (34,139,34))
            for child in children:
                if child != self.track_button: wx.CallAfter(child.Enable, False)
            try:
                self.trackstatus = True
                new.NewportKmirrorTracking(self, self.controller, self.socket[3], self.motor)
                logging.info('Rotator: Tracking started.')
            except:
                pass
        else:
            wx.CallAfter(self.track_button.SetLabel, "Start Tracking")
            wx.CallAfter(self.track_button.SetForegroundColour,(0,0,0))
            wx.CallAfter(self.Enable, True)
            for child in children:
                if child != self.track_button: wx.CallAfter(child.Enable, True)
            try:
                self.trackstatus = False
                sleep(1)
                new.NewportStop(self.controller, self.socket[2], self.motor)
                logging.info('Rotator: Motion stopped.')
            except ValueError:
                pass

    @run_async
    def on_timer(self, event):
        try:
            pa = new.NewportStatusGet(self.controller, self.socket[1], self.motor)[0]
            wx.CallAfter(self.curr_pa.SetLabel, u'%.3f \N{DEGREE SIGN}' % pa)
        except ValueError:
            pass
        

    @run_async
    def step_pos(self, event):
        wx.CallAfter(self.Enable, False)
        try:
            step = self.step_size.GetValue()
            info = new.NewportStatusGet(self.controller, self.socket[0], self.motor)
            pa = info[0] + step
            logging.info('Rotator: Move to %f' % (float(pa)) + u'\N{DEGREE SIGN}')
            new.NewportKmirrorMove(self.controller, self.socket[0], self.motor, self.jog_state, pa)
            logging.info('Rotator: Is at %f' % (float(pa)) + u'\N{DEGREE SIGN}')
        except ValueError:
            pass
        wx.CallAfter(self.Enable, True)

    @run_async
    def step_neg(self, event):
        wx.CallAfter(self.Enable, False)
        try:
            step = self.step_size.GetValue()
            info = new.NewportStatusGet(self.controller, self.socket[0], self.motor)
            pa = info[0] - step
            logging.info('Rotator: Move to %f' % (float(pa)) + u'\N{DEGREE SIGN}')
            new.NewportKmirrorMove(self.controller, self.socket[0], self.motor, self.jog_state, pa)
            logging.info('Rotator: Is at %f' % (float(pa)) + u'\N{DEGREE SIGN}')
        except ValueError:
            pass
        wx.CallAfter(self.Enable, True)

    @run_async
    def on_home(self, event):
        wx.CallAfter(self.Enable, False)
        try:
            new.NewportInitialize(self.controller, self.motor, self.socket[0], 0)
            logging.info('Rotator: Re-homing rotator')
        except:
            raise
        wx.CallAfter(self.Enable, True)
