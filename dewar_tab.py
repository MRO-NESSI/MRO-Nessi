#!/usr/bin/env python

import wx
import sys
import wx.lib.agw.floatspin as FS
import XPS_C8_drivers as xps
import threading as thr
import time
import math
# need to decide how to import this module
#from handlers import *
from configobj import ConfigObj

from wx.lib.pubsub import Publisher

# Handling a failure to connect to the controller.
def OnFail():
	'''A graceful exit with logging if the connection to the controller fails.  It will be logged in kmirrorlog.txt'''
	print 'Connection to Newport Controller has failed.\nPlease Check IP and Port.'
	sys.exit()
# Preparing an array to use for rotataion testing
diff_array=[]
for i in range(-100,101):
	diff_array.append(5*math.exp(-(i*.03)**2/2))
	
x=xps.XPS()
open_sockets=[]
used_sockets=[]
cfg = ConfigObj('nessisettings.ini')

#@timeout(30)
def fill_socket_list():
	for i in range(int(cfg['general']['sockets'])):
		open_sockets.append(x.TCP_ConnectToServer('192.168.0.254',5001,1))
	
	# Checking the status of the connections.
	for i in range(int(cfg['general']['sockets'])):
		if open_sockets[i] == -1:
			OnFail()
		else:
			pass
try:
	fill_socket_list()
except:
	pass

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
		# This displays the error string.
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
	for i in range(len(open_sockets)):
		x.TCP_CloseSocket(i)
	for i in range(len(used_sockets)):
		x.TCP_CloseSocket(i)
	
class KMirrorApp(wx.App):
	'''The K-Mirror testing app.'''	

	def OnInit(self):
		self.frame=KMirrorFrame(None, title='K-Mirror Testing Program')
		self.SetTopWindow(self.frame)
		self.frame.Show()
		return True

class KMirrorFrame(wx.Frame):
	'''The frame for the K-Mirror panel.  This contains three panels, one for each major set of functions.'''

	def __init__(self,*args,**kwargs):
		'''The initialization routine for this frame.  This establishes which panels will be displayed.'''
		super(KMirrorFrame,self).__init__(*args,**kwargs)
		# These are the panels to be included in the frame.
		self.notebook = NotebookDemo(self)
		self.SocketID=open_sockets.pop()
		used_sockets.append(self.SocketID)
		self.__DoLayout()
		self.SetInitialSize()
		# This binds the close event to the OnCLose function.
		self.Bind(wx.EVT_CLOSE,self.OnClose)
	
	# This function will handle the layout of the different elements of the program.
	def __DoLayout(self):
		'''A basic layout handler for the frame.  Layout information is available in KMIRRORREADME.'''
		# This establishes which layout manager we are using.
		sizer=wx.GridBagSizer()
		sizer.Add(self.notebook,(0,0))
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
			kill=x.KillAll(self.SocketID)
		# This checks to insure the kill command worked.  If it did not work, the standard error handler is called.
			if kill[0] != 0:
				XPSErrorHandler(SocketID, kill[0], 'KillAll')
			else:
				event.Skip()
				Publisher().sendMessage(('flag'),0)
				time.sleep(1)
				Close()
		else:
			# Vetoing the close event.
			event.Veto()

class NotebookDemo(wx.Notebook):
    def __init__(self,*args,**kwargs):
		super(NotebookDemo,self).__init__(*args,**kwargs)
		self.tabFour = JogWindow(self)
		self.AddPage(self.tabFour, 'K-Mirror')
		self.tabOne = KMirrorWindow(self)
		self.AddPage(self.tabOne, "Movement")
		self.tabTwo = DewarWindow(self)
		self.AddPage(self.tabTwo, "Dewar")
		self.tabThree = RotationWindow(self)
		self.AddPage(self.tabThree, 'Rotation')

class JogWindow(wx.Panel):
	def __init__(self,*args,**kwargs):
		super(JogWindow,self).__init__(*args,**kwargs)
		self.panel_zero=Jog(self)
		self.panel_one=Emergency(self)
		self.line_zero=wx.StaticLine(self,style=wx.LI_HORIZONTAL)
		self.__DoLayout()
		self.SetInitialSize()

	def __DoLayout(self):
		sizer=wx.GridBagSizer()
		sizer.Add(self.panel_zero,(0,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		sizer.Add(self.line_zero,(1,0),(1,1),wx.EXPAND,border=5)
		sizer.Add(self.panel_one,(2,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		self.SetSizer(sizer)


class RotationWindow(wx.Panel):
	def __init__(self,*args,**kwargs):
		super(RotationWindow,self).__init__(*args,**kwargs)
		self.panel_zero=Spin(self)
		self.panel_one=Emergency(self)
		self.line_zero=wx.StaticLine(self,style=wx.LI_HORIZONTAL)
		self.__DoLayout()
		self.SetInitialSize()

	def __DoLayout(self):
		sizer=wx.GridBagSizer()
		sizer.Add(self.panel_zero,(0,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		sizer.Add(self.line_zero,(1,0),(1,1),wx.EXPAND,border=5)
		sizer.Add(self.panel_one,(2,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		self.SetSizer(sizer)


class KMirrorWindow(wx.Panel):
	# A frame to hold the kmirror related frames.
	def __init__(self,*args,**kwargs):
		super(KMirrorWindow,self).__init__(*args,**kwargs)
		self.panel_zero=Emergency(self)
		self.panel_one=Information(self)
		self.panel_two=Control(self)
		# some decorative seperation between panels.
		self.line_zero=wx.StaticLine(self,style=wx.LI_HORIZONTAL)
		self.line_one=wx.StaticLine(self,style=wx.LI_HORIZONTAL)
		# calling the function that will define the layout for the frame.
		self.__DoLayout()
		self.SetInitialSize()

	def __DoLayout(self):
		sizer=wx.GridBagSizer()
		sizer.Add(self.panel_two,(0,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		sizer.Add(self.line_zero,(1,0),(1,1),wx.EXPAND,border=5)
		sizer.Add(self.panel_one,(2,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)  
		sizer.Add(self.line_one,(3,0),(1,1),wx.EXPAND,border=5)
		sizer.Add(self.panel_zero,(4,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		# This finalizes the layout.
		self.SetSizer(sizer)


class DewarWindow(wx.Panel):
	# A panel to hold the dewar controls.
	def __init__(self,*args,**kwargs):
		super(DewarWindow,self).__init__(*args,**kwargs)
		#self.info={'name':'button!'}
		self.panel1=ProbotixPanel(self)
		self.panel2=ProbotixPanel(self)
		self.panel3=ProbotixPanel(self)
		self.panel4=ProbotixPanel(self)
		self.panel5=ProbotixPanel(self)
		self.panel6=ProbotixPanel(self)
		self.panel0=Emergency(self)
		self.line0=wx.StaticLine(self,style=wx.LI_HORIZONTAL)
		self.__DoLayout()
		self.SetInitialSize()

	def __DoLayout(self):
		sizer=wx.GridBagSizer()
		sizer.Add(self.panel1,(0,0))
		sizer.Add(self.panel2,(0,1))
		sizer.Add(self.panel3,(1,0))
		sizer.Add(self.panel4,(1,1))
		sizer.Add(self.line0,(3,0),(1,2),wx.EXPAND,border=5)
		sizer.Add(self.panel0,(2,0),(1,1),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		self.SetSizer(sizer)

class ProbotixPanel(wx.Panel):
	def __init__(self,*args,**kwargs):
		super(ProbotixPanel,self).__init__(*args,**kwargs)
		print args
		self.info={'name':'Button!','wheel1':[60,'grism1'],'wheel2':[60,'grism2'],'wheel3':[60,'grism3'],'wheel4':[60,'grism4'],'wheel5':[60,'grism5'],'wheel6':[60,'grism6'],'wheel7':[60,'grism7'],'wheel8':[60,'grism8']}

		try:
			self.choices=[self.info['wheel1'][1],self.info['wheel2'][1],self.info['wheel3'][1],self.info['wheel4'][1],self.info['wheel5'][1],self.info['wheel6'][1],self.info['wheel7'][1],self.info['wheel8'][1]]
		except KeyError:
			self.choices=[]

		try:
			self.move=wx.Button(self,label='Move '+self.info['name'])
		except KeyError:
			self.move=wx.Button(self,label='blank')		

		self.option=wx.Choice(self,choices=self.choices)
		self.Bind(wx.EVT_CHOICE,self.OnSelect)
		self.Bind(wx.EVT_BUTTON,self.OnButton)
		self.__DoLayout()
		self.SetInitialSize()

	def OnButton(self,event):
			pass


	def OnSelect(self,event):
			pass

	def __DoLayout(self):
			sizer=wx.GridBagSizer()
			sizer.Add(self.option,(0,0))
			sizer.Add(self.move,(1,0))
			self.SetSizer(sizer)

class Emergency(wx.Panel):
	'''The Emergency controller panel, which changes which allows for an emergency stop of all motor movement.  The functions of this panel are blocking, but this does not affect functionality as no other commands need to be sent simultaneously and doing so could cause problems.'''

	def __init__(self,*args,**kwargs):
		'''Initialization of the Emergency panel.'''
		super(Emergency,self).__init__(*args,**kwargs)
###		self.mode='Enable'
		self.SocketID=open_sockets.pop()
		used_sockets.append(self.SocketID)
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
		# This is the kill all command.
		kill=x.KillAll(self.SocketID)
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
		self.SocketID=open_sockets.pop()
		used_sockets.append(self.SocketID)
		self.Group = 'Rotator'
		self.Positioner = self.Group + '.P1'
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
		else:
			self.pos.SetValue(str(position[1]))
		velocity=x.GroupVelocityCurrentGet(self.SocketID,self.Group,1)
		if velocity[0] != 0:
			XPSErrorHandler(self.SocketID, velocity[0], 'GroupVelocityCurrentGet')
		else:		
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
		self.SocketID1=open_sockets.pop()
		used_sockets.append(self.SocketID1)
		self.SocketID2=open_sockets.pop()
		used_sockets.append(self.SocketID2)
		self.home=[0]
		self.Group = 'Rotator'
		self.Positioner = self.Group + '.P1'
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
		else:		
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



class Spin(wx.Panel):
	'''This panel handles the controls for movement and allow the user to define the type of motion and the motion parameters.  The user can set the position to travel to, the velocity at which to travel as well as the acceleration of the motor and the minimum and maximum jerk time.'''

	def __init__(self,*args,**kwargs):
		'''The initialization function for the control panel including lables, radio buttons, float spinners, and a button.'''
		super(Spin,self).__init__(*args,**kwargs)
		# Titles and labels.
		self.mode=1
		Publisher().sendMessage(('probotix_state'),self.mode)
		self.title=wx.StaticText(self,label='Spin')
		self.label_three=wx.StaticText(self,label='Velocity')
		self.label_four=wx.StaticText(self,label='deg/s')
		self.label_five=wx.StaticText(self,label='Acceleration')
		self.label_six=wx.StaticText(self,label='deg/s^2')
		self.velocity=FS.FloatSpin(self,digits=6)
		self.acceleration=FS.FloatSpin(self,digits=6)
		self.jog_mode=wx.TextCtrl(self)
		# Defining newport specific information	
		self.SocketID1=open_sockets.pop()
		used_sockets.append(self.SocketID1)
		self.SocketID2=open_sockets.pop()
		used_sockets.append(self.SocketID2)
		self.home=[0]
		self.Group = 'Dewar'
		self.Positioner = self.Group + '.Pos'
		# The start up routine for motion which is as follows:
		# 1) kill all groups.
		# 2) initialize the group.
		# 3) home the group.
		# 4) retreive the profile information from the controller.
		self.GKill=x.GroupKill(self.SocketID1, self.Group)
		if self.GKill[0] != 0:
     			XPSErrorHandler(self.SocketID1, self.GKill[0], 'GroupKill')

		self.GInit=x.GroupInitialize(self.SocketID1, self.Group)
		if self.GInit[0] != 0:
     			XPSErrorHandler(self.SocketID1, self.GInit[0], 'GroupInitialize')
     
		self.GHomeSearch=x.GroupHomeSearchAndRelativeMove(self.SocketID1, self.Group,self.home)
		print self.GHomeSearch
		if self.GHomeSearch[0] != 0:
     			XPSErrorHandler(self.SocketID1, self.GHomeSearch[0], 'GroupHomeSearchAndRelativeMove')
		print self.Group
		
		self.profile=x.GroupSpinParametersGet(self.SocketID1,self.Group)
		print self.profile
		if self.profile[0] != 0:
				print self.profile
				XPSErrorHandler(self.SocketID1, self.profile[0], 'GroupSpinParametersGet')			
		# These commands set the values of the entry boxes to the stored setting on the motor.		
		else:		
			self.velocity.SetValue(self.profile[1])	
			self.acceleration.SetValue(self.profile[2])
		# Defining the button.
		self.jog_toggle=wx.Button(self,1,label='Toggle Mode')
		self.jog_set=wx.Button(self,2,label='Set Parameters')
		self.jog_stop=wx.Button(self,3,label='Stop')
		# Performing the layout.
		self.__DoLayout()
		# Binding the buttons to their events.
		self.Bind(wx.EVT_BUTTON, self.OnSet, id=2)
		self.Bind(wx.EVT_BUTTON, self.Ontoggle, id=1)
		self.Bind(wx.EVT_BUTTON, self.OnStop,id=3)

		self.SetInitialSize()

	# The layout handler for the control panel.
	def __DoLayout(self):
		'''A basic layout handler for Control panel.  Layout information is available in KMIRRORREADME.'''
		sizer=wx.GridBagSizer()
		sizer.Add(self.title,(0,0),(1,5),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		sizer.Add(self.label_three,(3,1))
		sizer.Add(self.label_four,(4,2))
		sizer.Add(self.label_five,(1,1))
		sizer.Add(self.label_six,(2,2))
		sizer.Add(self.velocity,(4,1))
		sizer.Add(self.jog_mode,(4,0))
		sizer.Add(self.jog_toggle,(3,0))
		sizer.Add(self.jog_set,(5,0))
		sizer.Add(self.jog_stop,(5,1))
		sizer.Add(self.acceleration,(2,1))
		self.SetSizer(sizer)
		self.thread_state=0
		Publisher().subscribe(self.update,('probotix_state'))
	
	# The button functionality for the control panel.
	def Ontoggle(self,event):		
		if self.mode == 0:
				self.jog_mode.SetValue('Enabled')
				self.mode = 1
				Publisher().sendMessage(('probotix_state'),0)			
			
		elif self.mode == 1:
				self.jog_mode.SetValue('Disabled')
				self.mode = 0
				Publisher().sendMessage(('probotix_state'),0)

		else:
			print 'Error in toggle function.'
	
	def OnSet(self,event):	

		if self.mode == 1:
			print self.thread_state
			if self.thread_state == 0:
				self.thread_state = 1
				task=SpinThread(self.SocketID2,self.Group)
				task.start()
			else:
				print 'thread passed'
			self.Gset=x.GroupSpinParametersSet(self.SocketID1, self.Positioner,float(self.velocity.GetValue()),float(self.acceleration.GetValue()))
			if self.Gset[0] != 0:
				XPSErrorHandler(self.SocketID1, self.Gset[0], 'GroupSpinParametersSet')
			else:
				pass
		else:
			wx.MessageBox('Spin mode is not enabled.',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)

	def OnStop(self,event):
		self.stop=x.GroupSpinModeStop(self.SocketID1,self.Group,100)

		if self.stop[0] != 0:
			XPSErrorHandler(self.SocketID1, self.stop[0], 'GroupSpinModeStop')
		else:
			pass

	
	def update(self,probotix_state):
		'''This function changes the movement state.'''
		self.thread_state=probotix_state.data
		print self.thread_state


class Jog(wx.Panel):
	'''This panel handles the controls for movement and allow the user to define the type of motion and the motion parameters.  The user can set the position to travel to, the velocity at which to travel as well as the acceleration of the motor and the minimum and maximum jerk time.'''

	def __init__(self,*args,**kwargs):
		'''The initialization function for the control panel including lables, radio buttons, float spinners, and a button.'''
		super(Jog,self).__init__(*args,**kwargs)
		# Titles and labels.
		self.mode=0
		self.profile=0
		Publisher().sendMessage(('probotix_state'),self.mode)
		self.title=wx.StaticText(self,label='Jog')
		self.label_three=wx.StaticText(self,label='Velocity')
		self.label_four=wx.StaticText(self,label='deg/s')
		self.label_five=wx.StaticText(self,label='Acceleration')
		self.label_six=wx.StaticText(self,label='deg/s^2')
		self.velocity=FS.FloatSpin(self,digits=6)
		self.acceleration=FS.FloatSpin(self,digits=6)
		self.jog_mode=wx.TextCtrl(self)
		# Defining newport specific information	
		self.SocketID1=open_sockets.pop()
		used_sockets.append(self.SocketID1)
		self.SocketID2=open_sockets.pop()
		used_sockets.append(self.SocketID2)
		self.SocketID3=open_sockets.pop()
		used_sockets.append(self.SocketID3)
		self.home=[0]
		self.Group = 'Rotator'
		self.Positioner = self.Group + '.P1'
		# The start up routine for motion which is as follows:
		# 1) kill all groups.
		# 2) initialize the group.
		# 3) home the group.
		# 4) retreive the profile information from the controller.
		self.GKill=x.GroupKill(self.SocketID1, self.Group)
		if self.GKill[0] != 0:
     			XPSErrorHandler(self.SocketID1, self.GKill[0], 'GroupKill')

		self.GInit=x.GroupInitialize(self.SocketID1, self.Group)
		if self.GInit[0] != 0:
     			XPSErrorHandler(self.SocketID1, self.GInit[0], 'GroupInitialize')
     
		self.GHomeSearch=x.GroupHomeSearchAndRelativeMove(self.SocketID1, self.Group,self.home)
		print self.GHomeSearch
		if self.GHomeSearch[0] != 0:
     			XPSErrorHandler(self.SocketID1, self.GHomeSearch[0], 'GroupHomeSearchAndRelativeMove')
		
		self.profile=x.GroupJogParametersGet(self.SocketID1,self.Group,1)
		print self.profile
		if self.profile[0] != 0:
				print self.profile
				XPSErrorHandler(self.SocketID1, self.profile[0], 'GroupJogParametersGet')			
		# These commands set the values of the entry boxes to the stored setting on the motor.		
		else:		
			self.velocity.SetValue(self.profile[1])	
			self.acceleration.SetValue(self.profile[2])
		# Defining the button.
		self.jog_toggle=wx.Button(self,1,label='Toggle Mode')
		self.jog_set=wx.Button(self,2,label='Set Parameters')
		self.jog_stop=wx.Button(self,3,label='Stop')
		self.mode_one=wx.RadioButton(self,-1,'use profile  ', style = wx.RB_GROUP)
		self.mode_two=wx.RadioButton(self,-1,'do not use profile  ')
		# Performing the layout.
		self.__DoLayout()
		# Binding the buttons to their events.
		self.Bind(wx.EVT_BUTTON, self.OnSet, id=2)
		self.Bind(wx.EVT_BUTTON, self.Ontoggle, id=1)
		self.Bind(wx.EVT_BUTTON, self.OnStop,id=3)
		self.Bind(wx.EVT_RADIOBUTTON,self.OnRadio)

		self.SetInitialSize()

	# The layout handler for the control panel.
	def __DoLayout(self):
		'''A basic layout handler for Control panel.  Layout information is available in KMIRRORREADME.'''
		sizer=wx.GridBagSizer()
		sizer.Add(self.title,(0,0),(1,5),wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
		sizer.Add(self.label_three,(3,1))
		sizer.Add(self.label_four,(4,2))
		sizer.Add(self.label_five,(1,1))
		sizer.Add(self.label_six,(2,2))
		sizer.Add(self.velocity,(4,1))
		sizer.Add(self.jog_mode,(4,0))
		sizer.Add(self.jog_toggle,(3,0))
		sizer.Add(self.jog_set,(5,0))
		sizer.Add(self.jog_stop,(5,1))
		sizer.Add(self.acceleration,(2,1))
		sizer.Add(self.mode_one,(2,0))
		sizer.Add(self.mode_two,(1,0))
		self.SetSizer(sizer)
		self.thread_state=0
		Publisher().subscribe(self.update,('jog_state'))
	
	# The button functionality for the control panel.
	def Ontoggle(self,event):		
		if self.mode == 0:
			self.Gmode=x.GroupJogModeEnable(self.SocketID1, self.Group)
			print self.Gmode
			if self.Gmode[0] != 0:
   				XPSErrorHandler(self.SocketID1, self.Gmode[0], 'GroupJogModeEnable')
			self.jog_mode.SetValue('Enabled')
			self.mode = 1
			Publisher().sendMessage(('jog_state'),0)			
			
		elif self.mode == 1:
			self.Gmode=x.GroupJogModeDisable(self.SocketID1, self.Group)
			print self.Gmode
			if self.Gmode[0] != 0:
				XPSErrorHandler(self.SocketID1, self.Gmode[0], 'GroupJogModeDisable')
			self.jog_mode.SetValue('Disabled')
			self.mode = 0
			Publisher().sendMessage(('jog_state'),0)

		else:
			print 'Error in toggle function.'
	
	def OnSet(self,event):	

		if self.mode == 1:
			if self.profile == 1:
				
				task=ProfileThread(self.SocketID3,self.Group)
				task.start()
			else:
				self.Gset=x.GroupJogParametersSet(self.SocketID1, self.Group,[float(self.velocity.GetValue())],[float(self.acceleration.GetValue())])
				if self.Gset[0] != 0:
	
					XPSErrorHandler(self.SocketID1, self.Gset[0], 'GroupJogParametersSet')
				else:
					pass
		else:
			wx.MessageBox('Jog mode is not enabled.',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)

	def OnStop(self,event):
		self.stop=x.GroupJogParametersSet(self.SocketID1,self.Group,[0],[100])
		Publisher().sendMessage(('profile_state'),0)
		if self.stop[0] != 0:
			XPSErrorHandler(self.SocketID1, self.stop[0], 'GroupJogModeStop')
		else:
			pass

	def OnRadio(self,event):
		'''This function sets the type of movement when the user clicks either of the butttons.'''
		if self.mode_one.GetValue()==True:
			self.profile=1
		elif self.mode_two.GetValue()==True:
			self.profile=0
		# This error mode should not be reachable from the UI.
		else:
			self.move_mode=-1
	
	def update(self,jog_state):
		'''This function changes the movement state.'''
		self.thread_state=jog_state.data
		print self.thread_state


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
		Publisher().subscribe(self.update,('flag'))
	
	# This function executes when the thread is called.
	def run(self):
		'''This is the function that runs when the thread is called. It uses a while loop to update the information in the info panel every .5 seconds.'''
		# The while loop that controls the updates.
		while self.state == 1:
			# The timer that determines how often the thread updates.
			time.sleep(.5)
			# The functions that retreives the information.
			pos=x.GroupPositionCurrentGet(self.socket,self.group,1)
			if pos[0] != 0:
				XPSErrorHandler(self.socket, pos[0], 'GroupPositionCurrentGet')
			else:
				app.frame.notebook.tabOne.panel_one.pos.SetValue(str(pos[1]))
			vel=x.GroupVelocityCurrentGet(self.socket,self.group,1)
			if vel[0] != 0:
				XPSErrorHandler(self.socket, vel[0], 'GroupVelocityCurrentGet')
			else:
				app.frame.notebook.tabOne.panel_one.vel.SetValue(str(vel[1]))
			# the function that checks to see if the movement state has changed.
			
	# This function actually changes the movement state.
	def update(self,flag):
		'''This function changes the movement state.'''
		self.state=flag.data


class SpinThread(thr.Thread):
	def __init__(self,socket,group):
		super(SpinThread,self).__init__()
		# Defining the necessary information for the newport controller. 
		self.socket=socket
		self.group=group
		self.state=0

	def run(self):
		
		time.sleep(1)
		
		while self.state == 0:
			time.sleep(.15)
			value = x.GPIODigitalGet(self.socket, 'GPIO4.DI')
			print value, bin(value[1])[::-1], self.state, bin(value[1])[::-1][8]
			if value[0] != 0:
				XPSErrorHandler(self.socket,value[0],'GPIODigitalGet')
			elif format(value[1],"016b")[::-1][8] == '1':
				self.state=1
			elif format(value[1],"016b")[::-1][9] == '0':
				self.state=2
			elif format(value[1],"016b")[::-1][10] == '0':
				self.state=3
			else:
				print 'passed'
			
		self.stop=x.GroupSpinModeStop(self.socket, self.group, 800)
		if self.stop[0] != 0:
			XPSErrorHandler(self.socket, self.stop[0], 'GroupSpinModeStop')
		else:
			Publisher().sendMessage(('probotix_state'),0)


class ProfileThread(thr.Thread):
	def __init__(self,socket,group):
		super(ProfileThread,self).__init__()
		# Defining the necessary information for the newport controller. 
		self.socket=socket
		self.group=group
		self.state=1
		self.check=Publisher().subscribe(self.update,('profile_state'))

	def run(self):
		
		for i in range(201):
			if self.state == 1:				
				print 'working'
				time.sleep(.5)
				self.Gset=x.GroupJogParametersSet(self.socket, self.group,[diff_array[i]],[300])
				if self.Gset[0] != 0:
					XPSErrorHandler(self.SocketID1, self.Gset[0], 'GroupJogParametersSet')
				else:
					pass
			else:
				pass


	def update(self,profile_state):
		self.state=profile_state.data
			
		

if __name__=='__main__':
	app=KMirrorApp(False)	
	app.MainLoop()

