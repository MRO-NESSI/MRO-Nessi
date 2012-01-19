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
		self.panel_zero=Master(self)
		self.panel_one=Information(self)
		self.panel_two=Control(self)
		self.line_zero=wx.StaticLine(self,style=wx.LI_HORIZONTAL)
		self.line_one=wx.StaticLine(self,style=wx.LI_VERTICAL)
		
		self.__DoLayout()
		self.SetInitialSize()
		self.Bind(wx.EVT_CLOSE,self.OnClose)
		self.OnOpen()

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
		else:
			event.Veto()

	def OnOpen(self):
		print 'I opened connections :D'
	
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
		#
#		
#		
#		ADD ALL OTHER SETTING CONTROLS
#
#
		#
		self.execute=wx.Button(self,label='Execute')
		self.__DoLayout()
		self.SetInitialSize()

	def __DoLayout(self):
		'''A basic layout handler for Control panel.'''
		sizer=wx.GridBagSizer()
		sizer.Add(self.title,(0,0))
		sizer.Add(self.execute,(1,0))
		self.SetSizer(sizer)

if __name__=='__main__':
	app=KMirrorApp(False)	
	app.MainLoop()

