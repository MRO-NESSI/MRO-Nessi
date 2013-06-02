import wx
import logging
import actuators.newport as new

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
        self.trackstatus = True
        self.jog_state = False
        new.NewportInitialize(self.controller, self.motor, self.socket[0], 0)
        
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
        self.Bind(wx.EVT_BUTTON, self.on_home, self.home_button)
    
#    def OnPower(self):
#        self.k_power = True
#        global k 
#        k = Kmirror()
#    
#    def OffPower(self):
#        self.k_power = False
#        self.curr_pa.SetLabel('...')
#        k.__del__()
        
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
            pa = float(self.new_pa.GetValue())
            logging.info('Rotator: Move to %f' % (float(pa)) + u'\N{DEGREE SIGN}')
            new.NewportKmirrorMove(self.controller, self.socket[0], self.motor, self.jog_state, pa)
            logging.info('Rotator: Is at %f' % (float(pa)) + u'\N{DEGREE SIGN}')
            
        except ValueError:
            pass
        
#       try:
#            if not self.k_power:
#                wx.Bell()
#                wx.MessageBox('The rotator does not have power.', style=wx.OK|wx.CENTER)
#            else:
#                pa = float(self.new_pa.GetValue())
#                pub.sendMessage("LOG EVENT", "Rotator: Move to %d" % (int(pa)%360) + u'\N{DEGREE SIGN}')
#                k.set_pa(pa)
#                pub.sendMessage("LOG EVENT", "Rotator: Is at %d" % (int(pa)%360) + u'\N{DEGREE SIGN}')
#        except ValueError:
#            pass # TODO: Error Message

    def on_track(self, event):
        pass
#        try:
#            if not self.k_power:
#                wx.Bell()
#                wx.MessageBox('The rotator does not have power.', style=wx.OK|wx.CENTER)
#            else:
#                pub.sendMessage("LOG EVENT", "K-Mirror is Tracking...")
#                self.trackstatus = True
#                self.track_thread = TrackThread(self)
#                self.track_thread.daemon=True
#                self.track_thread.start()
#            
#        except ValueError:
#            pass

    def on_stop(self, event):
        pass
#        try:
#            if not self.k_power:
#                wx.Bell()
#                wx.MessageBox('The rotator does not have power.', style=wx.OK|wx.CENTER)
#            else:
#                pub.sendMessage("LOG EVENT", "K-Mirror Stopped...")
#                self.trackstatus = False
#        except ValueError:
#            pass

    def on_timer(self, event):
        try:
            pa = new.NewportStatusGet(self.controller, self.socket[1], self.motor)[0]
            self.curr_pa.SetLabel(str(pa) + u'\N{DEGREE SIGN}')
        except ValueError:
            pass
#        try:
#            if not self.k_power:
#                pass
#            else:
#                pa = k.get_pa()
#                self.curr_pa.SetLabel(str(pa) + u'\N{DEGREE SIGN}')
#        except ValueError:
#            pass
    
    def step_pos(self, event):
        try:
            step = self.step_size.GetValue()
            info = new.NewportStatusGet(self.controller, self.socket[0], self.motor)
            pa = info[0] + step
            logging.info('Rotator: Move to %f' % (float(pa)) + u'\N{DEGREE SIGN}')
            new.NewportKmirrorMove(self.controller, self.socket[0], self.motor, self.jog_state, pa)
            logging.info('Rotator: Is at %f' % (float(pa)) + u'\N{DEGREE SIGN}')
        except ValueError:
            pass
#            if not self.k_power:
#                wx.Bell()
#                wx.MessageBox('The rotator does not have power.', style=wx.OK|wx.CENTER)
#            else:
#                step = self.step_size.GetValue()
#                pa = k.get_pa() + step
#                pub.sendMessage("LOG EVENT", "Stepping rotator +")
#                k.set_pa(pa)
#                pub.sendMessage("LOG EVENT", "Rotator moved +" + str(step))
#        except ValueError:
#            pass

    def step_neg(self, event):
        try:
            step = self.step_size.GetValue()
            info = new.NewportStatusGet(self.controller, self.socket[0], self.motor)
            pa = info[0] - step
            logging.info('Rotator: Move to %f' % (float(pa)) + u'\N{DEGREE SIGN}')
            new.NewportKmirrorMove(self.controller, self.socket[0], self.motor, self.jog_state, pa)
            logging.info('Rotator: Is at %f' % (float(pa)) + u'\N{DEGREE SIGN}')
        except ValueError:
            pass
#        try:
#            if not self.k_power:
#                wx.Bell()
#                wx.MessageBox('The rotator does not have power.', style=wx.OK|wx.CENTER)
#            else:
#                step = self.step_size.GetValue()
#                pa = k.get_pa() - step
#                pub.sendMessage("LOG EVENT", "Stepping rotator -")
#                k.set_pa(pa)
#                pub.sendMessage("LOG EVENT", "Rotator moved -" + str(step))
#        except ValueError:
#            pass

    def on_home(self, event):
        try:
            new.NewportInitialize(self.controller, self.motor, self.socket[0], 0)
            logging.info('Rotator: Re-homing rotator')
        except:
            raise
