#!/usr/bin/env python

# kmirror.py
# Matt Napolitano
# Created: 01/18/2012

#################################
#
# As of 03/20/2012 this program runs correctly.
#
#################################

'''
kmirror.py created on 01/18/2012 by Matt Napolitano.
----------------------------------------------------
This is a GUI designed to aid the testing of the Newport rotation stage RV350PP through the Newport XPS-C8 controller.
This program will allow for absolute moving, relative moving, and speed variation.
For full details refer to KMIRRORREADME.
----------------------------------------------------
'''

import wx
import sys
import wx.lib.agw.floatspin as FS
import XPS_C8_drivers as xps
import threading as thr
import time
from wx.lib.pubsub import Publisher

def OnFail():
	print 'Connection to Newport Controller has failed.\nPlease Check IP and Port.'
	sys.exit()

x=xps.XPS()
socket1=x.TCP_ConnectToServer('192.168.0.254',5001,1)
socket2=x.TCP_ConnectToServer('192.168.0.254',5001,1)
socket3=x.TCP_ConnectToServer('192.168.0.254',5001,1)

if socket1 == -1 or socket2 == -1 or socket3 == -1:
	OnFail()

def XPSErrorHandler(socket,code,name):
	if code != -2 and code != -108:
		error=x.ErrorStringGet(socket,code)
		if error[0] != 0:
			choice=wx.MessageBox(name +' : ERROR '+ str(code),style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
		else:
			choice=wx.MessageBox(name +' : '+ error[1],style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
	else:
		if code == -2:
			choice=wx.MessageBox(name +' : TCP timeout',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
		elif code == -108:
			choice=wx.MessageBox(name +' : The TCP/IP connection was closed by an administrator',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)

def Close():
		
		x.TCP_CloseSocket(socket1)
		x.TCP_CloseSocket(socket2)
		x.TCP_CloseSocket(socket3)

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
			Publisher().sendMessage(('flag'),0)
			time.sleep(1)
			Close()
		else:
			event.Veto()
	
class Master(wx.Panel):
	'''The Master controller panel, which changes states for the program and device.'''
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
		'''A basic layout handler for Emergency Panel.'''
		sizer=wx.GridBagSizer()
		sizer.Add(self.title,(0,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL)
		sizer.Add(self.line,(1,0),(1,1),wx.EXPAND)
		sizer.Add(self.kill_group,(2,0))
		self.SetSizer(sizer)

	def OnButton(self,event):
		SocketID=socket1
		kill=x.KillAll(SocketID)
		if kill[0] != 0:
			XPSErrorHandler(SocketID, kill[0], 'KillAll')
		else:
			result=wx.MessageBox('All Groups Killed.\nProgram Must Be Restarted.',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)	
			if result == wx.OK:
				sys.exit()
			else:
				sys.exit()
				

class Information(wx.Panel):
	def __init__(self,*args,**kwargs):
		super(Information,self).__init__(*args,**kwargs)
		self.title=wx.StaticText(self,label='Information')
		self.label_one=wx.StaticText(self,label='Position')
		self.label_two=wx.StaticText(self,label='deg')
		self.label_three=wx.StaticText(self,label='Velocity')
		self.label_four=wx.StaticText(self,label='deg/s')
		self.pos=wx.TextCtrl(self)
		self.vel=wx.TextCtrl(self)
		self.read=wx.Button(self,label='Manual Read')
		self.SocketID=socket2

		###################################
		self.Group = 'GROUP1'
		self.Positioner = self.Group + '.POSITIONER'
		###################################
		
		self.Bind(wx.EVT_BUTTON, self.OnButton)
		self.__DoLayout()
		self.SetInitialSize()

	def __DoLayout(self):
		'''A basic layout handler for Information panel.'''
		sizer=wx.GridBagSizer()
		sizer.Add(self.title,(0,0),(1,4),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		sizer.Add(self.label_one,(1,0),(1,2),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		sizer.Add(self.label_two,(2,1))
		sizer.Add(self.label_three,(1,2),(1,2),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		sizer.Add(self.label_four,(2,3))
		sizer.Add(self.pos,(2,0))
		sizer.Add(self.vel,(2,2))
		sizer.Add(self.read,(3,0),(1,4),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		self.SetSizer(sizer)

	def OnButton(self,event):
		position=x.GroupPositionCurrentGet(self.SocketID,self.Group,1)
		if position[0] != 0:
			XPSErrorHandler(self.SocketID, position[0], 'GroupPositionCurrentGet')
		velocity=x.GroupVelocityCurrentGet(self.SocketID,self.Group,1)
		if velocity[0] != 0:
			XPSErrorHandler(self.SocketID, velocity[0], 'GroupVelocityCurrentGet')
		self.pos.SetValue(str(position[1]))
		self.vel.SetValue(str(velocity[1]))

class Control(wx.Panel):
	def __init__(self,*args,**kwargs):
		super(Control,self).__init__(*args,**kwargs)

		self.title=wx.StaticText(self,label='Control')
		self.label_one=wx.StaticText(self,label='Position')
		self.label_two=wx.StaticText(self,label='deg')
		self.label_three=wx.StaticText(self,label='Velocity')
		self.label_four=wx.StaticText(self,label='deg/s')
		self.label_five=wx.StaticText(self,label='Acceleration')
		self.label_six=wx.StaticText(self,label='deg/s^2')
		self.label_seven=wx.StaticText(self,label='Min Jerk Time')
		self.label_eight=wx.StaticText(self,label='sec')
		self.label_nine=wx.StaticText(self,label='Max Jerk Time')
		self.label_ten=wx.StaticText(self,label='sec')
		self.position=FS.FloatSpin(self,digits=6)
		self.velocity=FS.FloatSpin(self,digits=6)
		self.acceleration=FS.FloatSpin(self,digits=6)
		self.jerk1=FS.FloatSpin(self,digits=6)
		self.jerk2=FS.FloatSpin(self,digits=6)

		self.mode_one=wx.RadioButton(self,-1,'Move Relative  ', style = wx.RB_GROUP)
		self.mode_two=wx.RadioButton(self,-1,'Move Absolute  ')
		
		self.move_mode=0		#Mode 0 is relative and mode 1 is absolute. -1 is error.
		
		
		#########  XPS Specific Calls  ##########
		
		self.SocketID_A=socket2
		self.SocketID=socket3
		self.home=[0]
	
		self.Group = 'GROUP1'
		self.Positioner = self.Group + '.POSITIONER'
		
		self.GKill=x.GroupKill(self.SocketID, self.Group)
		if self.GKill[0] != 0:
     			XPSErrorHandler(self.SocketID, self.GKill[0], 'GroupKill')

		self.GInit=x.GroupInitialize(self.SocketID, self.Group)
		if self.GInit[0] != 0:
     			XPSErrorHandler(self.SocketID, self.GInit[0], 'GroupInitialize')
     
		self.GHomeSearch=x.GroupHomeSearchAndRelativeMove(self.SocketID, self.Group,self.home)
		if self.GHomeSearch[0] != 0:
     			XPSErrorHandler(self.SocketID, self.GHomeSearch[0], 'GroupHomeSearchAndRelativeMove')
		
		self.profile=x.PositionerSGammaParametersGet(self.SocketID,self.Positioner)
		if self.profile[0] != 0:
				XPSErrorHandler(self.SocketID, self.profile[0], 'PositionerSGammaParametersGet')
			
			
		#########################################
		
		self.velocity.SetValue(self.profile[1])	
		self.acceleration.SetValue(self.profile[2])	
		self.jerk1.SetValue(self.profile[3])	
		self.jerk2.SetValue(self.profile[4])		

		self.execute=wx.Button(self,label='Execute')
		self.__DoLayout()
		self.Bind(wx.EVT_BUTTON, self.OnButton)
		self.Bind(wx.EVT_RADIOBUTTON,self.OnRadio)
		self.SetInitialSize()

	def __DoLayout(self):
		'''A basic layout handler for Control panel.'''
		sizer=wx.GridBagSizer()
		sizer.Add(self.title,(0,0),(1,5),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		sizer.Add(self.label_one,(1,1))
		sizer.Add(self.label_two,(2,2),(1,1),wx.ALIGN_CENTER_HORIZONTAL)
		sizer.Add(self.label_three,(3,1))
		sizer.Add(self.label_four,(4,2))
		sizer.Add(self.label_five,(1,3))
		sizer.Add(self.label_six,(2,4))
		sizer.Add(self.label_seven,(3,3))
		sizer.Add(self.label_eight,(4,4),(1,1),wx.ALIGN_CENTER_HORIZONTAL)
		sizer.Add(self.label_nine,(5,3))
		sizer.Add(self.label_ten,(6,4),(1,1),wx.ALIGN_CENTER_HORIZONTAL)
		sizer.Add(self.mode_one,(1,0),(1,1),wx.ALIGN_CENTER_VERTICAL)
		sizer.Add(self.mode_two,(2,0),(1,1),wx.ALIGN_CENTER_VERTICAL)
		sizer.Add(self.velocity,(4,1))
		sizer.Add(self.position,(2,1))
		sizer.Add(self.execute,(4,0))
		sizer.Add(self.acceleration,(2,3))
		sizer.Add(self.jerk1,(4,3))
		sizer.Add(self.jerk2,(6,3))
		self.SetSizer(sizer)

	def OnButton(self,event):
		'''This button will initiate motion and begin automatic tracking of position and movement.'''
		
		if self.move_mode == 0 or self.move_mode == 1:

			info=InfoThread(self.SocketID_A,self.Group)
			info.start()
			
			result=x.PositionerSGammaParametersSet(self.SocketID,self.Positioner,self.velocity.GetValue(),self.acceleration.GetValue(),self.jerk1.GetValue(),self.jerk2.GetValue())

			if result[0] != 0:
				XPSErrorHandler(self.SocketID, result[0], 'PositionerSGammaParametersSet')	

			else:
				task=ControlThread(self.SocketID,self.Group,self.position.GetValue(),self.move_mode)
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
	
class ControlThread(thr.Thread):
	def __init__(self,socket,group,val,mode):
		super(ControlThread,self).__init__()
		self.socket=socket
		self.group=group
		self.val=val
		self.mode=mode
		
	def run(self):
		if self.mode == 0:
			move=x.GroupMoveRelative(self.socket,self.group,[self.val])
			if move[0] != 0:
				XPSErrorHandler(self.socket, move[0], 'GroupMoveRelative')
		elif self.mode == 1:
			move=x.GroupMoveAbsolute(self.socket,self.group,[self.val])
			if move[0] != 0:
				XPSErrorHandler(self.socket, move[0], 'GroupMoveAbsolute')

class InfoThread(thr.Thread):
	def __init__(self,socket,group):
		super(InfoThread,self).__init__()
		self.socket=socket
		self.group=group
		self.state=1

	def run(self):
		while self.state == 1:
			time.sleep(.5)
			pos=x.GroupPositionCurrentGet(self.socket,self.group,1)
			if pos[0] != 0:
				XPSErrorHandler(self.socket, pos[0], 'GroupPositionCurrentGet')
			vel=x.GroupVelocityCurrentGet(self.socket,self.group,1)
			if vel[0] != 0:
				XPSErrorHandler(self.socket, vel[0], 'GroupVelocityCurrentGet')
			app.frame.panel_one.pos.SetValue(str(pos[1]))
			app.frame.panel_one.vel.SetValue(str(vel[1]))
			Publisher().subscribe(self.update,('flag'))
	
	def update(self,flag):
		self.state=flag.data

if __name__=='__main__':
	app=KMirrorApp(False)	
	app.MainLoop()

