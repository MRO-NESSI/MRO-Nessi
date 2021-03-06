#!/usr/bin/env python

import sys
import wx
import wx.lib.agw.floatspin as FS
import instrument.actuators.XPS_C8_drivers as xps
import time
import math
import instrument.actuators.newport as new
from gui.overviewtab.fpapanel import FPAPanel
from threadtools import timeout, TimeoutError

x = xps.XPS()

@timeout(10)
def socket_list():
    s = []
    for i in range(5):
        s.append(x.TCP_ConnectToServer('192.168.0.254',5001,1))
   
    for i in range(5):
        if s[i] == -1:
            print 'XPS socet connections failed.'
            sys.exit()
    return s

try:
    s = socket_list()
except TimeoutError:
    print "XPS connection timed out."
    sys.exit()
    

class FPA(wx.App):
    '''The FPA focusing app.''' 

    def OnInit(self):
        self.frame=FPAFrame(None, title='FPA Focusing Program')
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

class FPAFrame(wx.Frame):
    def __init__(self,*args,**kwargs):
        super(FPAFrame,self).__init__(*args,**kwargs)
        p = wx.Panel(self)
        self.panel0 = FPAPanel(self,'array', x,s[1:])
        self.panel1 = Emergency(self)
        self.__DoLayout()
        self.SetInitialSize()

    # This function will handle the layout of the different elements of the program.
    def __DoLayout(self):
        '''A basic layout handler for the frame.'''
        # This establishes which layout manager we are using.
        sizer=wx.GridBagSizer()
        sizer.Add(self.panel0,(0,0),(1,1))
        sizer.Add(self.panel1,(1,0),(1,1))
        self.SetSizer(sizer)
    

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
        sizer.Add(self.kill_group,(2,0),(1,1))
        self.SetSizer(sizer)
    
    def OnButton(self,event):
        kill=x.KillAll(s[2])
        if kill[0] != 0:
            new.XPSErrorHandler(x, s[0], kill[0], 'KillAll')
        else:
            result=wx.MessageBox('All groups killed.\nMotors must be reinitialized',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK) 
 
if __name__ == '__main__':
    app=FPA(False)   
    app.MainLoop()  
