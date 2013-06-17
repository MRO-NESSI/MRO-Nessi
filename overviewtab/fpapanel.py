import wx
import logging
import actuators.newport as new
import wx.lib.agw.floatspin as FS

class FPAPanel(wx.Panel):
    def __init__(self, parent, motor, controller, socket):
        #wx.Panel.__init__(self, parent, *args, **kwargs)
        super(FPAPanel, self).__init__(parent)

        self.controller = controller
        self.socket = socket
        self.motor = motor
        try:
            new.NewportInitialize(self.controller, self.motor, self.socket[0], 0)
        except TypeError:
            pass
        else:
            self.pa = 0
        # Attributes
#        self.curr_pa_text = wx.StaticText(self, label="Current :")
#        self.curr_pa = wx.StaticText(self, label="...")
        self.new_pa_text = wx.StaticText(self, label="New Pos "+u"\u00B5"+"m:")


        self.step_p = wx.Button(self, size=(30,-1), label="+")
        self.step_m = wx.Button(self, size=(30,-1), label="-")
        self.set_button = wx.Button(self,  size=(62,-1), label="Set")
        self.stop_button = wx.Button(self,  size=(62,-1), label="Stop")
        self.home_button = wx.Button(self, size=(62,-1), label="Home")      
        self.step_txt = wx.StaticText(self, label="Step Size "+u"\u00B5"+"m:")
        self.step_size = FS.FloatSpin(self,digits=6)
        self.position=FS.FloatSpin(self,digits=6)
        self.position.SetRange(0,15000)
        self.step_size.SetRange(0, 500)
        self.step_size.SetValue(1)
                
        # Layout
        self.__DoLayout()
        
        # Event handlers
        self.Bind(wx.EVT_BUTTON, self.step_pos, self.step_p)
        self.Bind(wx.EVT_BUTTON, self.step_neg, self.step_m)
        self.Bind(wx.EVT_BUTTON, self.on_set, self.set_button)
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.stop_button)
        self.Bind(wx.EVT_BUTTON, self.on_home, self.home_button)
        self.SetInitialSize()

    def __DoLayout(self):
        sizer = wx.GridBagSizer()
        sizer.Add(self.position, (1,1), (1,1))
        sizer.Add(self.set_button,  pos=(1,2), span=(1,2), flag=wx.ALIGN_LEFT)
        sizer.Add(self.new_pa_text, (1,0))
        sizer.Add(self.step_m, pos=(2,2), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.step_p, pos=(2,3), flag=wx.ALIGN_LEFT)
        
        sizer.Add(self.step_txt, pos=(2,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.step_size, pos=(2,1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.stop_button,  pos=(3,1), flag=wx.ALIGN_LEFT)
        sizer.Add(self.home_button,  pos=(3,2), span=(1,2), flag=wx.ALIGN_LEFT)

        # Add the grid bag to the static box and make everything fit
        self.SetSizer(sizer)
        

    def on_set(self, event):
        try:
            
            move = self.pa-self.position.GetValue()
            if move == 0:
                pass
            else:
                speed = 10**math.floor(math.log10(math.fabs(move))) 
                direction = math.copysign(1,move)           
                NewportFocusMove(self.controller, self.socket[0], self.motor, move, speed, 1)
#            logging.info('')
#            new.NewportKmirrorMove(self.controller, self.socket[0], self.motor, self.jog_state, pa)
            logging.info('')
            
        except ValueError:
            pass
        
    def on_stop(self, event):
#        new.NewportFocusStop(self.controller, self.socket[1:], self.motor)
        pass
    
    def step_pos(self, event):
        try:
            step = self.step_size.GetValue()
            speed = 10**math.floor(math.log10(math.fabs(step))) 
            direction = math.copysign(1,step)   
#            info = new.NewportStatusGet(self.controller, self.socket[0], self.motor)
#            pa = info[0] + step
            logging.info('')
#            new.NewportKmirrorMove(self.controller, self.socket[0], self.motor, self.jog_state, pa)
            logging.info('')
        except ValueError:
            pass

    def step_neg(self, event):
        try:
            step = self.step_size.GetValue()
            speed = 10**math.floor(math.log10(math.fabs(step))) 
            direction = math.copysign(1,step)   
#            info = new.NewportStatusGet(self.controller, self.socket[0], self.motor)
#            pa = info[0] - step
            logging.info('')
#            new.NewportKmirrorMove(self.controller, self.socket[0], self.motor, self.jog_state, pa)
            logging.info('')
        except ValueError:
            pass

    def on_home(self, event):
        try:
#            new.NewportInitialize(self.controller, self.motor, self.socket[0], 0)
            logging.info('')
        except:
            raise
