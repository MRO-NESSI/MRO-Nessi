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
This is a GUI designed to aid the testing of the Newport rotation stage RV350HAT-F through the Newport XPS-C8 controller.
This program will allow for absolute moving, relative moving, speed variation, acceleration control, and jerk time control.
This program will display current position and velocity when moving.
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

# Handling a failure to connect to the controller.
def OnFail():
	'''A graceful exit with logging if the connection to the controller fails.  It will be logged in kmirrorlog.txt'''
	print 'Connection to Newport Controller has failed.\nPlease Check IP and Port.'
	sys.exit()

# Opening three sockets to the controller, one socket per thread.
x=xps.XPS()
socket1=x.TCP_ConnectToServer('192.168.0.254',5001,1)
socket2=x.TCP_ConnectToServer('192.168.0.254',5001,1)
socket3=x.TCP_ConnectToServer('192.168.0.254',5001,1)

# Checking the status of the connections.
if socket1 == -1 or socket2 == -1 or socket3 == -1:
	OnFail()

# General error handling for the Newport controller functions
def XPSErrorHandler(socket,code,name):
	'''This is a general error handling function for the newport controller functions. First the function checks for errors in communicating with the controller, then it fetches the error string and displays it in a message box.  If the error string can not be found it will print the error code for lookup by the user.  This function will log the errors in kmirrorlog.txt'''

	# This checks to see if the error is in communication with the controller.
	if code != -2 and code != -108:

		# Getting the error string.
		error=x.ErrorStringGet(socket,code)
		# If the error string lookup fails, this message will display with the error code.
		if error[0] != 0:
			choice=wx.MessageBox(name +' : ERROR '+ str(code),style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
`		# This displays the error string.
		else:
			choice=wx.MessageBox(name +' : '+ error[1],style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
	# This code handles the case where the connection to the controller fails after initial contact.
	else:
		if code == -2:
			choice=wx.MessageBox(name +' : TCP timeout',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
		elif code == -108:
			choice=wx.MessageBox(name +' : The TCP/IP connection was closed by an administrator',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)

# A function to close the connections when the program is closing.
def Close():
	'''This function closes the connections to the newport controller.'''
	x.TCP_CloseSocket(socket1)
	x.TCP_CloseSocket(socket2)
	x.TCP_CloseSocket(socket3)

# The app that will contain all the different windows and panels for the kmirror test program.
class KMirrorApp(wx.App):
	'''The K-Mirror testing app.'''	

	def OnInit(self):
		self.frame=KMirrorFrame(None, title='K-Mirror Testing Program')
		self.SetTopWindow(self.frame)
		self.frame.Show()
		return True

# This is the frame containing all the panels and controls for the GUI.
class KMirrorFrame(wx.Frame):
	'''The frame for the K-Mirror panel.  This contains three panels, one for each major set of functions.'''

	def __init__(self,*args,**kwargs):
		'''The initialization routine for this frame.  This establishes which panels will be displayed.'''
		super(KMirrorFrame,self).__init__(*args,**kwargs)
		# These are the panels to be included in the frame.
		self.panel_zero=Emergency(self)
		self.panel_one=Information(self)
		self.panel_two=Control(self)
		# some decorative seperation between panels.
		self.line_zero=wx.StaticLine(self,style=wx.LI_HORIZONTAL)
		self.line_one=wx.StaticLine(self,style=wx.LI_HORIZONTAL)
		# calling the function that will define the layout for the frame.
		self.__DoLayout()
		self.SetInitialSize()
		# This binds the close event to the OnCLose function.
		self.Bind(wx.EVT_CLOSE,self.OnClose)
	
	# This function will handle the layout of the different elements of the program.
	def __DoLayout(self):
		'''A basic layout handler for the frame.  Layout information is available in KMIRRORREADME.'''
		# This establishes which layout manager we are using.
		sizer=wx.GridBagSizer()
		# These define the position of all elements of the frame where (0,0) is the top left position.
		# (x,y) is defined with x being the vertical position and y being the horizontal position.
		sizer.Add(self.panel_two,(0,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		sizer.Add(self.line_zero,(1,0),(1,1),wx.EXPAND,border=5)
		sizer.Add(self.panel_one,(2,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)  
		sizer.Add(self.line_one,(3,0),(1,1),wx.EXPAND,border=5)
		sizer.Add(self.panel_zero,(4,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		# This finalizes the layout.
		self.SetSizer(sizer)
	
	# This function is called when the program is closed and first confirms closing then stops all tasks and closes the program.
	def OnClose(self,event):
		'''This is a function that confirms the choice to close and then kills all groups and closes all connections.'''
		# A message box that asks the user to confirm the choice to close the program.
		result=wx.MessageBox('Are you sure you want to close this window?',style=wx.CENTER|wx.ICON_QUESTION|wx.YES_NO)
		
		# These conditionals make sure the user wants to exit the program.  It will only exit if the user chooses the yes option.
		if result == wx.NO:
			# Vetoing the close event.
			event.Veto()
		elif result == wx.YES:
			# This will let the close event occur after it sends the stop flag for the threads and closes the connections to the controller.
			event.Skip()
			Publisher().sendMessage(('flag'),0)
			time.sleep(1)
			Close()
		else:
			# Vetoing the close event.
			event.Veto()

# This class defines the functionality of the Emergency panel, which is in control of sending emergency stop commands to motors.	
class Emergency(wx.Panel):
	'''The Emergency controller panel, which changes which allows for an emergency stop of all motor movement.  The functions of this panel are blocking, but this does not affect functionality as no other commands need to be sent simultaneously and doing so could cause problems.'''

	def __init__(self,*args,**kwargs):
		'''Initialization of the Emergency panel.'''
		super(Emergency,self).__init__(*args,**kwargs)
###		self.mode='Enable'
		self.title=wx.StaticText(self,label='Emergency')
		# This defines the button characteristics for the 'kill all' button.
		self.kill_group=wx.Button(self,label='KILL ALL')
		self.kill_group.SetBackgroundColour(wx.Colour(255,0, 0))
		self.kill_group.ClearBackground()
		self.kill_group.Refresh()   
		# A line to seperate the title from the rest of the panel.  This is purely aesthetic.
		self.line=wx.StaticLine(self,style=wx.LI_HORIZONTAL)
		# This performs final layout and binding for functionality.
		self.__DoLayout()
		self.Bind(wx.EVT_BUTTON,self.OnButton)
		self.SetInitialSize()

	# Defining the layout of the emergency panel.	
	def __DoLayout(self):
		'''A basic layout handler for Emergency Panel.  Layout information is available in KMIRRORREADME.'''
		sizer=wx.GridBagSizer()
		sizer.Add(self.title,(0,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL)
		sizer.Add(self.line,(1,0),(1,1),wx.EXPAND)
		sizer.Add(self.kill_group,(2,0))
		self.SetSizer(sizer)
	
	# Defining what the button in the emergency panel will do.
	def OnButton(self,event):
		'''This button will send the emergency stop command to all running motors.'''
		# This defines which channel the controller and panel will communicate over.
		SocketID=socket3
		# This is the kill all command.
		kill=x.KillAll(SocketID)
		# This checks to insure the kill command worked.  If it did not work, the standard error handler is called.
		if kill[0] != 0:
			XPSErrorHandler(SocketID, kill[0], 'KillAll')
		# If the command worked, a message is displayed telling the user that it was succesful and that the program needs to be restarted before it can be used again. When the user accepts the message, the program is terminated.
		else:
			result=wx.MessageBox('All Groups Killed.\nProgram Must Be Restarted.',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)	
			if result == wx.OK:
				sys.exit()
			else:
				sys.exit()
				
# This panel holds the information readouts from the controller.
class Information(wx.Panel):
	'''This panel is responsible for holding readouts from the newport controller via the information thread.  The readouts include position and velocity.'''
	
	def __init__(self,*args,**kwargs):
		'''Initialization for the information panel including labels, text controls, and a button.'''
		super(Information,self).__init__(*args,**kwargs)
		# Title and labels.
		self.title=wx.StaticText(self,label='Information')
		self.label_one=wx.StaticText(self,label='Position')
		self.label_two=wx.StaticText(self,label='deg')
		self.label_three=wx.StaticText(self,label='Velocity')
		self.label_four=wx.StaticText(self,label='deg/s')
		# Text boxes for output from the controller.
		self.pos=wx.TextCtrl(self)
		self.vel=wx.TextCtrl(self)
		# A button for manual reading from the controller.
		self.read=wx.Button(self,label='Manual Read')
		# setting the newport information.
		self.SocketID=socket2
		self.Group = 'GROUP1'
		self.Positioner = self.Group + '.POSITIONER'
		# Binding the manual read button to its functions.
		self.Bind(wx.EVT_BUTTON, self.OnButton)
		# Finalizing the layout.
		self.__DoLayout()
		self.SetInitialSize()

	# The layout manager for the information handler.
	def __DoLayout(self):
		'''A basic layout handler for Information panel.  Layout information is available in KMIRRORREADME.'''
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

	# Defining button functionality.
	def OnButton(self,event):
		# These commands retreive the position and velocity information from the controller and handle errors.
		position=x.GroupPositionCurrentGet(self.SocketID,self.Group,1)
		if position[0] != 0:
			XPSErrorHandler(self.SocketID, position[0], 'GroupPositionCurrentGet')
		velocity=x.GroupVelocityCurrentGet(self.SocketID,self.Group,1)
		if velocity[0] != 0:
			XPSErrorHandler(self.SocketID, velocity[0], 'GroupVelocityCurrentGet')
		# These commands will set the value in the readout to be the retreived values.
		self.pos.SetValue(str(position[1]))
		self.vel.SetValue(str(velocity[1]))

# The panel which handles tho commands for movement.
class Control(wx.Panel):
	'''This panel handles the controls for movement and allow the user to define the type of motion and the motion parameters.  The user can set the position to travel to, the velocity at which to travel as well as the acceleration of the motor and the minimum and maximum jerk time.'''

	def __init__(self,*args,**kwargs):
		'''The initialization function for the control panel including lables, radio buttons, float spinners, and a button.'''
		super(Control,self).__init__(*args,**kwargs)
		# Titles and labels.
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
		# Float spinners for entering values.  These can have arbitrary precision, and currently have six decimal places of precision.
		self.position=FS.FloatSpin(self,digits=6)
		self.velocity=FS.FloatSpin(self,digits=6)
		self.acceleration=FS.FloatSpin(self,digits=6)
		self.jerk1=FS.FloatSpin(self,digits=6)
		self.jerk2=FS.FloatSpin(self,digits=6)
		# Radio buttons to choose the type of motion to be executed. Mode 0 is relative motion and mode 1 is absolute motion. -1 is an error.
		self.mode_one=wx.RadioButton(self,-1,'Move Relative  ', style = wx.RB_GROUP)
		self.mode_two=wx.RadioButton(self,-1,'Move Absolute  ')		
		self.move_mode=0			
		# Defining newport specific information	
		self.SocketID1=socket1
		self.SocketID2=socket2
		self.home=[0]
		self.Group = 'GROUP1'
		self.Positioner = self.Group + '.POSITIONER'
		# The start up routine for motion which is as follows:
		# 1) kill all groups.
		# 2) initialize the group.
		# 3) home the group.
		# 4) retreive the profile information from the controller.
		self.GKill=x.GroupKill(self.SocketID2, self.Group)
		if self.GKill[0] != 0:
     			XPSErrorHandler(self.SocketID2, self.GKill[0], 'GroupKill')

		self.GInit=x.GroupInitialize(self.SocketID2, self.Group)
		if self.GInit[0] != 0:
     			XPSErrorHandler(self.SocketID2, self.GInit[0], 'GroupInitialize')
     
		self.GHomeSearch=x.GroupHomeSearchAndRelativeMove(self.SocketID2, self.Group,self.home)
		if self.GHomeSearch[0] != 0:
     			XPSErrorHandler(self.SocketID2, self.GHomeSearch[0], 'GroupHomeSearchAndRelativeMove')
		
		self.profile=x.PositionerSGammaParametersGet(self.SocketID2,self.Positioner)
		if self.profile[0] != 0:
				XPSErrorHandler(self.SocketID2, self.profile[0], 'PositionerSGammaParametersGet')			
		# These commands set the values of the entry boxes to the stored setting on the motor.		
		self.velocity.SetValue(self.profile[1])	
		self.acceleration.SetValue(self.profile[2])	
		self.jerk1.SetValue(self.profile[3])	
		self.jerk2.SetValue(self.profile[4])
		# Defining the button.
		self.execute=wx.Button(self,label='Execute')
		# Performing the layout.
		self.__DoLayout()
		# Binding the buttons to their events.
		self.Bind(wx.EVT_BUTTON, self.OnButton)
		self.Bind(wx.EVT_RADIOBUTTON,self.OnRadio)
		self.SetInitialSize()

	# The layout handler for the control panel.
	def __DoLayout(self):
		'''A basic layout handler for Control panel.  Layout information is available in KMIRRORREADME.'''
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

	# The button functionality for the control panel.
	def OnButton(self,event):
		'''This button will initiate motion and begin automatic tracking of position and movement.'''
		
		# This checks to see if there has been an error in choosing motion type. If so an error message will appear in a window.
		if self.move_mode == 0 or self.move_mode == 1:
			# This starts the live information tracking thread in the information panel.
			info=InfoThread(self.SocketID1,self.Group)
			info.start()
			# This function sets the parameters of motion in the controller to the user defined input.  This uses the standard error handling.			
			result=x.PositionerSGammaParametersSet(self.SocketID2,self.Positioner,self.velocity.GetValue(),self.acceleration.GetValue(),self.jerk1.GetValue(),self.jerk2.GetValue())
			if result[0] != 0:
				XPSErrorHandler(self.SocketID2, result[0], 'PositionerSGammaParametersSet')	
			# If the parameter setting works then motion is initiated with the control thread.
			else:
				task=ControlThread(self.SocketID2,self.Group,self.position.GetValue(),self.move_mode)
				task.start()					
		else:
			result=wx.MessageBox('Button Malfunction in Control Panel.',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
		
	# This defines functionality for the radio buttons.
	def OnRadio(self,event):
		'''This function sets the type of movement when the user clicks either of the butttons.'''
		if self.mode_one.GetValue()==True:
			self.move_mode=0
		elif self.mode_two.GetValue()==True:
			self.move_mode=1
		# This error mode should not be reachable from the UI.
		else:
			self.move_mode=-1

# The thread for movement commands.	
class ControlThread(thr.Thread):
	'''This thread will communicate with the newport controller to initiate motion.  It takes input in the form thread(socket,group,movement_value,movement_mode)'''

	def __init__(self,socket,group,val,mode):
		'''This function initializes the parameters for the function calls as given by the main program.'''
		super(ControlThread,self).__init__()
		# Defining the necessary information for the newport controller. 
		self.socket=socket
		self.group=group
		self.val=val
		self.mode=mode
		
	def run(self):
		'''This is the set of functions that are executed when the thread is started.  These consist of either relative or absolute motion.'''
		# This code is executed if the relative motion option is chosen.
		if self.mode == 0:
			move=x.GroupMoveRelative(self.socket,self.group,[self.val])
			if move[0] != 0:
				XPSErrorHandler(self.socket, move[0], 'GroupMoveRelative')
			else:
				Publisher().sendMessage(('flag'),0)
		# This code is executed if the absolute motion option is chosen.
		elif self.mode == 1:
			move=x.GroupMoveAbsolute(self.socket,self.group,[self.val])
			if move[0] != 0:
				XPSErrorHandler(self.socket, move[0], 'GroupMoveAbsolute')
			else:
				Publisher().sendMessage(('flag'),0)

# This thread is used to poll the controller for information and update the UI.
class InfoThread(thr.Thread):
	'''This thread polls the controller for current position and velocity.  It takes input in the form thread(socket,group), it runs until it detects a change in run state.'''

	def __init__(self,socket,group):
		'''This function initializes the socket, group, and run state for the thread.'''
		super(InfoThread,self).__init__()
		self.socket=socket
		self.group=group
		self.state=1

	# This function executes when the thread is called.
	def run(self):
		'''This is the function that runs when the thread is called. It uses a while loop to update the information in the info panel every .5 seconds.'''
		# The while loop that controls the updates.
		while self.state == 1:
			# The timer that determines how often the thread updates.
			time.sleep(.5)
			# The functions that retreive the information.
			pos=x.GroupPositionCurrentGet(self.socket,self.group,1)
			if pos[0] != 0:
				XPSErrorHandler(self.socket, pos[0], 'GroupPositionCurrentGet')
			vel=x.GroupVelocityCurrentGet(self.socket,self.group,1)
			if vel[0] != 0:
				XPSErrorHandler(self.socket, vel[0], 'GroupVelocityCurrentGet')
			# The functions that update the information panel.
			app.frame.panel_one.pos.SetValue(str(pos[1]))
			app.frame.panel_one.vel.SetValue(str(vel[1]))
			# the function that checks to see if the movement state has changed.
			Publisher().subscribe(self.update,('flag'))
	# This function actually changes the movement state.
	def update(self,flag):
		'''This function changes the movement state.'''
		self.state=flag.data

# This code is a standard way to only put up a GUI if the program was run as opposed to imported in another program.
if __name__=='__main__':
	app=KMirrorApp(False)	
	app.MainLoop()

