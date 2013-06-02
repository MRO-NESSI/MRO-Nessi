#!/usr/bin/env python

import wx
import wx.lib.agw.floatspin as FS
import XPS_C8_drivers as xps
import time
import math
import actuators.newport as new
from overviewtab.fpapanel.py import FPAPanel

x = xps.XPS()
s0 = x.TCP_ConnectToServer('192.168.0.254',5001,1)
s1 = x.TCP_ConnectToServer('192.168.0.254',5001,1)
s2 = x.TCP_ConnectToServer('192.168.0.254',5001,1)
s3 = x.TCP_ConnectToServer('192.168.0.254',5001,1)
s4 = x.TCP_ConnectToServer('192.168.0.254',5001,1)

class FPA(wx.App):
    '''The Fpa focusing app.''' 

    def OnInit(self):
        self.frame=FPA(None, title='FPA Focusing Program')
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

class FPAFrame(wx.Frame):
    def __init__(self,*args,**kwargs):
        super(FPAFrame,self).__init__(*args,**kwargs)
        self.panel0 = FPAPanel(frame, x,[s1,s2,s3,s4],'array')
        self.panel1 = Emergency()
        self.__DoLayout()
        self.SetInitialSize()
        self.Bind(wx.EVT_CLOSE,self.OnClose)
    
    # This function will handle the layout of the different elements of the program.
    def __DoLayout(self):
        '''A basic layout handler for the frame.  Layout information is available in KMIRRORREADME.'''
        # This establishes which layout manager we are using.
        sizer=wx.GridBagSizer()
        sizer.Add(self.panel0,(0,0))
        sizer.Add(self.panel1,(1,0))
        self.SetSizer(sizer)
    
    # This function is called when the program is closed and first confirms closing then stops all tasks and closes the program.
    def OnClose(self,event):
        kill=x.KillAll(s2)
        if kill[0] != 0:
            new.XPSErrorHandler(x,s0, kill[0], 'KillAll')
        else:
            Close()

class Emergency(wx.Panel):
    def __init__(self,*args,**kwargs):
        '''Initialization of the Emergency panel.'''
        super(Emergency,self).__init__(*args,**kwargs)
        self.title=wx.StaticText(self,label='Emergency')
        self.kill_group=wx.Button(self,label='KILL ALL')
        self.kill_group.SetBackgroundColour(wx.Colour(255,0, 0))
        self.kill_group.ClearBackground()
        self.kill_group.Refresh()   
        self.line=wx.StaticLine(self,style=wx.LI_HORIZONTAL)
        self.__DoLayout()
        self.Bind(wx.EVT_BUTTON,self.OnButton)
        self.SetInitialSize()

    def __DoLayout(self):
        sizer=wx.GridBagSizer()
        sizer.Add(self.title,(0,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL)
        sizer.Add(self.line,(1,0),(1,1),wx.EXPAND)
        sizer.Add(self.kill_group,(2,0))
        self.SetSizer(sizer)
    
    def OnButton(self,event):
        kill=x.KillAll(s2)
        if kill[0] != 0:
            new.XPSErrorHandler(x, s0, kill[0], 'KillAll')
        else:
            result=wx.MessageBox('All groups killed.\nMotors must be reinitialized',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)    
