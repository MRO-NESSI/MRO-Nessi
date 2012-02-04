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
This program will allow for absolute moving, relative moving, and speed variation.
For full details refer to README_KMIRROR.
----------------------------------------------------
'''

import wx
import sys
import wx.lib.agw.floatspin as FS
import XPS_C8_drivers as xps
import threading as thr






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
		self.line_one=wx.StaticLine(self,style=wx.LI_HORIZONTAL)
		self.__DoLayout()
		self.SetInitialSize()
		self.Bind(wx.EVT_CLOSE,self.OnClose)

	def __DoLayout(self):
		'''A basic layout handler.'''
		sizer=wx.GridBagSizer()
		sizer.Add(self.panel_two,(0,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		sizer.Add(self.line_zero,(1,0),(1,1),wx.EXPAND,border=5)
		sizer.Add(self.panel_one,(2,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)  
		sizer.Add(self.line_one,(3,0),(1,1),wx.EXPAND,border=5)
		sizer.Add(self.panel_zero,(4,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		
		self.SetSizer(sizer)

	def OnClose(self,event):
		'''A message on closing to confirm choice and then kills all groups and closes all connections.'''
		result=wx.MessageBox('Are you sure you want to close this window?',style=wx.CENTER|wx.ICON_QUESTION|wx.YES_NO)
		
		if result == wx.NO:
			event.Veto()
		elif result == wx.YES:
			event.Skip()
			self.panel_two.Close()
		else:
			event.Veto()
	
class Master(wx.Panel):
	''''The Master controller panel, which changes states for the program and device.''''
	def __init__(self,*args,**kwargs):
		super(Master,self).__init__(*args,**kwargs)
		self.mode='Enable'
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
		''''A basic layout handler for Emergency Panel.''''
		sizer=wx.GridBagSizer()
		sizer.Add(self.title,(0,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL)
		sizer.Add(self.line,(1,0),(1,1),wx.EXPAND)
		sizer.Add(self.kill_group,(2,0))
		self.SetSizer(sizer)

	def OnButton(self,event):
		SocketID=app.frame.panel_two.SocketID3
		kill=app.frame.panel_two.x.KillAll(SocketID)
		if kill[0] != 0:
			self.XPSErrorHandler(SocketID, kill[0], 'KillAll')
		else:
			result=wx.MessageBox('All Groups Killed.\nProgram Must Be Restarted.',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)		

	def XPSErrorHandler(socket,code,name):
		if code != -2 and code != -108:
			error=app.frame.panel_two.x.ErrorStringGet(socket,code)
			if error[0] != 0:
				choice=wx.MessageBox(name +' : ERROR '+ str(code),style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
			else:
				choice=wx.MessageBox(name +' : '+ error[1],style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
		else:
			if code == -2:
				choice=wx.MessageBox(name +' : TCP timeout',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
			elif code == -108:
				choice=wx.MessageBox(name +' : The TCP/IP connection was closed by an administrator',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
	
class Information(wx.Panel):
	def __init__(self,*args,**kwargs):
		super(Information,self).__init__(*args,**kwargs)
		self.title=wx.StaticText(self,label='Information')
		###################################
		self.Group = 'GROUP1'
		self.Positioner = self.Group + '.POSITIONER'
		###################################
		self.__DoLayout()
		self.SetInitialSize()
		print self.SocketID 

	def __DoLayout(self):
		'''A basic layout handler for Information panel.'''
		sizer=wx.GridBagSizer()
		sizer.Add(self.title,(0,0))
		self.SetSizer(sizer)

	def Close(self):
		print 'panel_one'
		app.frame.x.TCP_CloseSocket(self.SocketID)

	def XPSErrorHandler(self,socket,code,name):
		if code != -2 and code != -108:
			error=app.frame.x.ErrorStringGet(socket,code)
			if error[0] != 0:
				choice=wx.MessageBox(name +' : ERROR '+ str(code),style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
			else:
				choice=wx.MessageBox(name +' : '+ error[1],style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
		else:
			if code == -2:
				choice=wx.MessageBox(name +' : TCP timeout',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
			elif code == -108:
				choice=wx.MessageBox(name +' : The TCP/IP connection was closed by an administrator',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)

class Control(wx.Panel):
	def __init__(self,*args,**kwargs):
		super(Control,self).__init__(*args,**kwargs)

		self.title=wx.StaticText(self,label='Control')
		self.label_one=wx.StaticText(self,label='Travel Speed')
		self.label_two=wx.StaticText(self,label='deg/s')
		self.label_three=wx.StaticText(self,label='Travel Position')
		self.label_four=wx.StaticText(self,label='deg')
		self.speed=FS.FloatSpin(self,digits=6)
		self.position=FS.FloatSpin(self,digits=6)

		self.mode_one=wx.RadioButton(self,-1,'Move Relative  ', style = wx.RB_GROUP)
		self.mode_two=wx.RadioButton(self,-1,'Move Absolute  ')
		
		self.move_mode=0		#Mode 0 is relative and mode 1 is absolute. -1 is error.

		#########  XPS Specific Calls  ##########
		
		
		self.home=[0]

		self.x=xps.XPS()
		self.SocketID1=self.x.TCP_ConnectToServer('192.168.0.254',5001,1)
		self.SocketID2=self.x.TCP_ConnectToServer('192.168.0.254',5001,1)
		self.SocketID3=self.x.TCP_ConnectToServer('192.168.0.254',5001,1)
		self.SocketID=self.SocketID1
	
		if self.SocketID1 == -1 or self.SocketID2 == -1 or self.SocketID3 == -1:
			self.OnFail()
			
		self.Group = 'GROUP1'
		self.Positioner = self.Group + '.POSITIONER'
		
		self.GKill=app.frame.x.GroupKill(self.SocketID, self.Group)
		if self.GKill[0] != 0:
     			self.XPSErrorHandler(self.SocketID, self.GKill[0], 'GroupKill')
     
		self.GInit=app.frame.x.GroupInitialize(self.SocketID, self.Group)
		if self.GInit[0] != 0:
     			self.XPSErrorHandler(self.SocketID, self.GInit[0], 'GroupInitialize')
     
		self.GHomeSearch=app.frame.x.GroupHomeSearchAndRelativeMove(self.SocketID, self.Group,self.home)
		if self.GHomeSearch[0] != 0:
     			self.XPSErrorHandler(self.SocketID, self.GHomeSearch[0], 'GroupHomeSearchAndRelativeMove')

		self.profile=app.frame.x.PositionerSGammaParametersGet(self.SocketID,self.Positioner)
		if self.profile[0] != 0:
			self.XPSErrorHandler(self.SocketID, self.profile[0], 'PositionerSGammaParametersGet')	
			
		#########################################

		self.execute=wx.Button(self,label='Execute')
		self.__DoLayout()
		self.Bind(wx.EVT_BUTTON, self.OnButton)
		self.Bind(wx.EVT_RADIOBUTTON,self.OnRadio)
		self.SetInitialSize()
		print self.SocketID 

	def __DoLayout(self):
		'''A basic layout handler for Control panel.'''
		sizer=wx.GridBagSizer()
		sizer.Add(self.title,(0,0),(1,3),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		sizer.Add(self.label_one,(1,1))
		sizer.Add(self.label_two,(2,2),(1,1),wx.ALIGN_CENTER_HORIZONTAL)
		sizer.Add(self.label_three,(3,1))
		sizer.Add(self.label_four,(4,2))
		sizer.Add(self.mode_one,(1,0),(1,1),wx.ALIGN_CENTER_VERTICAL)
		sizer.Add(self.mode_two,(2,0),(1,1),wx.ALIGN_CENTER_VERTICAL)
		sizer.Add(self.speed,(2,1))
		sizer.Add(self.position,(4,1))
		sizer.Add(self.execute,(4,0))
		self.SetSizer(sizer)

	def OnButton(self,event):
		'''Defining button functionality.'''
		if self.move_mode == 0 or self.move_mode == 1:
			
			result=app.frame.x.PositionerSGammaParametersSet(self.SocketID,self.Positioner,self.speed.GetValue(),self.profile[2],self.profile[3],self.profile[4])

			if result[0] != 0:
				self.XPSErrorHandler(self.SocketID, returns[0], 'PositionerSGammaParametersSet')	

			else:
				task=ControlThread(app,self.SocketID,self.Group,self.position.GetValue(),self.move_mode)
				task.start()
			
		else:
			result=wx.MessageBox('Button Malfunction in Control Panel.',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
		

	def OnRadio(self,event):

		if self.mode_one.GetValue()==True:
			self.move_mode=0

		elif self.mode_two.GetValue()==True:
			self.move_mode=1

		else:
			self.move_mode=-1
	
	def OnFail(self):
		result=wx.MessageBox('Connection to Newport Controller has failed.\nPlease Check IP and Port.',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)

		if result == wx.OK:
			sys.exit()

		else:
			sys.exit()

	def Close(self):
		
		self.x.TCP_CloseSocket(self.SocketID1)
		self.x.TCP_CloseSocket(self.SocketID2)
		self.x.TCP_CloseSocket(self.SocketID3)
			
		print 'panel two closed'

	def XPSErrorHandler(self,socket,code,name):
		if code != -2 and code != -108:
			error=self.x.ErrorStringGet(socket,code)
			if error[0] != 0:
				choice=wx.MessageBox(name +' : ERROR '+ str(code),style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
			else:
				choice=wx.MessageBox(name +' : '+ error[1],style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
		else:
			if code == -2:
				choice=wx.MessageBox(name +' : TCP timeout',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
			elif code == -108:
				choice=wx.MessageBox(name +' : The TCP/IP connection was closed by an administrator',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)

class ControlThread(thr.Thread):
	def __init__(self,app,socket,group,val,mode):
		super(ControlThread,self).__init__()
		self.app=app
		self.socket=socket
		self.group=group
		self.val=val
		self.mode=mode
		
	def run(self):
		if self.mode == 0:
			move=self.app.frame.x.GroupMoveRelative(self.socket,self.group,[self.val])
			if move[0] != 0:
				self.app.frame.panel_two.XPSErrorHandler(self.socket, move[0], 'GroupMoveRelative')
		elif self.mode == 1:
			move=self.app.frame.x.GroupMoveAbsolute(self.socket,self.group,[self.val])
			if move[0] != 0:
				self.app.frame.panel_two.XPSErrorHandler(self.socket, move[0], 'GroupMoveAbsolute')


if __name__=='__main__':
	app=KMirrorApp(False)	
	app.MainLoop()

