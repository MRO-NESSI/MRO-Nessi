#!/usr/bin/env python

# kmirror.py
# Matt Napolitano
# Created: 01/18/2012

#################################
#
# Fix borders, add buttons and controls to control.  work on info panel.  Implement slider/TextCTRL combo for speed of rotation.
#
#################################

'''
kmirror.py created on 01/18/2012 by Matt Napolitano.
----------------------------------------------------
This is a GUI designed to aid the testing of the Newport rotation stage RV350PP through the Newport XPS-C8 controller.
This program will allow for absolute moving, relative moving, continuous rotation as well as speed variation.
For full details refer to README_KMIRROR.
----------------------------------------------------
'''

import wx
import sys
#import XPS_C8_drivers as xps

class KMirrorApp(wx.App):
	'''The K-Mirror testing app.'''	
	def OnInit(self):
		self.frame=KMirrorFrame(None, title='K-Mirror Testing Program')
		self.SetTopWindow(self.frame)
		self.frame.Show()
		return True

class KMirrorFrame(wx.Frame):
	'''The frame for the K-Mirror panel.'''
	def __init__(self,*args,**kwargs):
		super(KMirrorFrame,self).__init__(*args,**kwargs)
		self.run_mode=-1
		#self.x=xps.XPS()
		#self.SocketID=x.TCP_ConnectToServer('192.168.0.254',5001,1)
		#if self.SocketID == -1:
		#	self.run_mode = -1
		#
		self.panel_zero=Master(self)
		self.panel_one=Information(self)
		self.panel_two=Control(self)
		self.line_zero=wx.StaticLine(self,style=wx.LI_HORIZONTAL)
		self.line_one=wx.StaticLine(self,style=wx.LI_VERTICAL)
		
		self.__DoLayout()
		self.SetInitialSize()
		self.Bind(wx.EVT_CLOSE,self.OnClose)
		
		if self.run_mode == -1:
			self.OnFail()

	def __DoLayout(self):
		'''A basic layout handler.'''
		sizer=wx.GridBagSizer()
		sizer.Add(self.panel_zero,(0,0),(1,3),wx.EXPAND,border=5)  
		sizer.Add(self.line_zero,(1,0),(1,3),wx.EXPAND,border=5)
		sizer.Add(self.panel_one,(2,0),border=5)
		sizer.Add(self.line_one,(2,1),border=5)
		sizer.Add(self.panel_two,(2,2),border=5)
		self.SetSizer(sizer)

	def OnClose(self,event):
		'''A message on closing to confirm choice and then kills all groups and closes all connections.'''
		result=wx.MessageBox('Are you sure you want to close this window?',style=wx.CENTER|wx.ICON_QUESTION|wx.YES_NO)
		
		if result == wx.NO:
			event.Veto()
		elif result == wx.YES:
			event.Skip()
			#self.x.TCP_CloseSocket(SocketID)
		else:
			event.Veto()

	def OnFail(self):
		result=wx.MessageBox('Connection to Newport Controller has failed.\nPlease Check IP and Port.\n\nContinue without functionality?',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.YES_NO)
		if result == wx.YES:
			print 'fail mode'

		elif result == wx.NO:
			sys.exit()

		else:
			sys.exit()

	
class Master(wx.Panel):
	'''The Master controller panel, which changes states for the program and device.'''
	def __init__(self,*args,**kwargs):
		super(Master,self).__init__(*args,**kwargs)
		self.title=wx.StaticText(self,label='Master')
		self.move_enable=wx.Button(self,label='enable')
		self.kill_group=wx.Button(self,label='kill group')
		self.line=wx.StaticLine(self,style=wx.LI_HORIZONTAL)
		self.__DoLayout()
		self.SetInitialSize()
		
	def __DoLayout(self):
		'''A basic layout handler for Master Panel.'''
		sizer=wx.GridBagSizer()
		sizer.Add(self.title,(0,0),(1,5),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		sizer.Add(self.line,(1,0),(1,4),wx.EXPAND)
		sizer.Add(self.move_enable,(2,1))
		sizer.Add(self.kill_group,(2,3))
		self.SetSizer(sizer)

class Information(wx.Panel):
	def __init__(self,*args,**kwargs):
		super(Information,self).__init__(*args,**kwargs)
		self.title=wx.StaticText(self,label='Information')
		self.__DoLayout()
		self.SetInitialSize()

	def __DoLayout(self):
		'''A basic layout handler for Information panel.'''
		sizer=wx.GridBagSizer()
		sizer.Add(self.title,(0,0))
		self.SetSizer(sizer)

class Control(wx.Panel):
	def __init__(self,*args,**kwargs):
		super(Control,self).__init__(*args,**kwargs)
		self.title=wx.StaticText(self,label='Control')
		self.speed=wx.TextCtrl(self)
		self.move=wx.TextCtrl(self)
		self.mode_one=wx.RadioButton(self,-1,'Move Relative', style = wx.RB_GROUP)
		self.mode_two=wx.RadioButton(self,-1,'Move Absolute')
		self.mode_three=wx.RadioButton(self,-1,'Move Spindle')

		#
#		
#		
#		ADD ALL OTHER SETTING CONTROLS
#
#
		#
		self.execute=wx.Button(self,label='Execute')
		self.__DoLayout()
		#self.Bind(wx.EVT_BUTTON, self.OnButton)
		self.SetInitialSize()

	def __DoLayout(self):
		'''A basic layout handler for Control panel.'''
		sizer=wx.GridBagSizer()
		sizer.Add(self.title,(0,0))
		sizer.Add(self.mode_one,(1,0))
		sizer.Add(self.mode_two,(2,0))
		sizer.Add(self.mode_three,(3,0))
		sizer.Add(self.execute,(4,1))
		sizer.Add(self.speed,(1,1))
		sizer.Add(self.move,(2,1))
		self.SetSizer(sizer)

if __name__=='__main__':
	app=KMirrorApp(False)	
	app.MainLoop()

