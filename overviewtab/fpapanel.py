import wx
import logging
import actuators.newport as new
import wx.lib.agw.floatspin as FS
import math
from threadtools import run_async

class FPAPanel(wx.Panel):
    def __init__(self, parent, motor, controller, socket):
        #wx.Panel.__init__(self, parent, *args, **kwargs)
        super(FPAPanel, self).__init__(parent)

        self.controller = controller
        self.socket = socket
        self.motor = motor

        try:
            new.NewportInitialize(self.controller, self.motor, self.socket[0], 0)
            new.NewportFocusHome(self.controller, self.socket[0], self.motor)
        except TypeError:
            pass
        else:
            self.pa = 0

        self.new_pa_text = wx.StaticText(self, label="New Pos "+u"\u00B5"+"m:")


        self.step_p = wx.Button(self, id=1, size=(30,-1), label="+")
        self.step_m = wx.Button(self, id=2, size=(30,-1), label="-")
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
        self.Bind(wx.EVT_BUTTON, self.on_step, self.step_p)
        self.Bind(wx.EVT_BUTTON, self.on_step, self.step_m)
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
        
    @run_async
    def on_set(self, event):
        try: 
            move = self.pa-self.position.GetValue()
            if move == 0:
                pass
            else:
                speed = 10**math.floor(math.log10(math.fabs(move))) 
                direction = math.copysign(1,move)           
                new.NewportFocusMove(self.controller, self.socket[0], self.motor, move, speed, direction)

        except ValueError:
            pass

    @run_async     
    def on_stop(self, event):
        try:
            new.NewportStop(self.controller, self.socket[1:], self.motor) 
        except:
            pass        
        children = self.GetChildren()
        for child in children:
            wx.CallAfter(child.Enable, True)
    
    @run_async
    def on_step(self, event):
        """
"""
        children = self.GetChildren()
        for child in children:
            if child != self.stop_button: wx.CallAfter(child.Enable, False)
        #wx.CallAfter(self.Enable, False)
        move = self.step_size.GetValue()

        if event.GetId() == 1:
            dierection = 1
        elif event.GetId() == 2:
            direction = -1
        else:
            return

        try:
            step = self.step_size.GetValue()
            speed = 10**math.floor(math.log10(math.fabs(step)))   
            new.NewportFocusMove(self.controller, self.socket[0], self.motor, move, speed, direction)
        except ValueError:
            pass
        for child in children:
            wx.CallAfter(child.Enable, True)

    @run_async
    def on_home(self, event):
        try:
            new.NewportFocusHome(self.controller, self.socket[0], self.motor)
        except:
            raise
