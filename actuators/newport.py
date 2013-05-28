#!/usr/bin/env python

import math
import XPS_C8_drivers as xps
from configobj import ConfigObj
from wx.lib.pubsub import Publisher
import threading as thr
import time

# Shared resources for programs that call these functions.
x=xps.XPS()
open_sockets=[]
used_sockets=[]
cfg = ConfigObj(infile='/home/mnapolitano/nessi/nessisettings.ini')
for i in range(int(cfg['general']['sockets'])):
	open_sockets.append(x.TCP_ConnectToServer('192.168.0.254',5001,1))
	
for i in range(int(cfg['general']['sockets'])):
	if open_sockets[i] == -1:
		print 'Error, Sockets not opened.'


def XPSErrorHandler(controller,socket,code,name):
	'''This is a general error handling function for the newport controller functions. First the function checks for errors in communicating with the controller, then it fetches the error string and displays it in a message box.  If the error string can not be found it will print the error code for lookup by the user.'''

	# This checks to see if the error is in communication with the controller.
	if code != -2 and code != -108:

		# Getting the error string.
		error=controller.ErrorStringGet(socket,code)
		# If the error string lookup fails, this message will display with the error code.
		if error[0] != 0:
			choice=wx.MessageBox(name +' : ERROR '+ str(code),style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
		# This displays the error string.
		else:
			print error[1] #choice=wx.MessageBox(name +' : '+ error[1],style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
	# This code handles the case where the connection to the controller fails after initial contact.
	else:
		if code == -2:
			choice=wx.MessageBox(name +' : TCP timeout',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
		elif code == -108:
			choice=wx.MessageBox(name +' : The TCP/IP connection was closed by an administrator',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)
		

#@threaded
def NewportWheelThread(controller,wheel,socket,current,position,home):
	'''
A thread that initiates a move in the dewar and then monitors The Newport GPIO for a bit flip that indicates the motor needs to be stopped.

	Inputs:	controller, name, socket, position, home.

	controller:	[xps]	Which instance of the XPS controller to use.
	wheel:		[str]	The name of the motor that is being used.  This is for config file purposes.
	socket:		[int]	Which socket to use to communicate with the XPS controller.
	current:	[int]	What position the motor is currently at.
	position:	[int]	What position the motor should move to.
	home:		[bool]	Determines whether the thread will find the home position or a different position.
'''
	# Initializing variables.
	controller=controller
	group=cfg[wheel]['group']
	socket=socket
	state=0
	# Different initializations depending on whether it is homing or not.
	if home == True:
		val=int(cfg[wheel]['home']['val'])
		bit=int(cfg[wheel]['home']['bit'])
		diff=1
	else:
		val=int(cfg[wheel]['position']['val'])
		bit=int(cfg[wheel]['position']['bit'])
		# self.diff is how many positions away from current the target position is.
		diff=(int(cfg[wheel]['slots'])-current+position)%int(cfg[wheel]['slots'])

	if current != position:
		# Starting motion.
		Gset=controller.GroupSpinParametersSet(socket,cfg[wheel]['group'],100,200)
		# Checking if the motion command was sent correctly.
		# If so then the GPIO checking begins.
		if Gset[0] != 0:
			XPSErrorHandler(controller ,socket, Gset[0], 'GroupSpinParametersSet')
		else:
			# A pause to let the motor begin moving before tracking it.
			# This prevents the counter from catching the bit flip before motion begins.
			time.sleep(1)
			# This while loop runs until the motor is one position before the target.
			# It has a one second delay after catching a bit flip to allow the motor to go past the switch so it is not double counted.
			while state < diff-1:
				time.sleep(.15)
				value = controller.GPIODigitalGet(socket, 'GPIO4.DI')
				if value[0] != 0:
					XPSErrorHandler(controller,socket,value[0],'GPIODigitalGet')
				elif int(format(value[1],"016b")[::-1][bit]) == val:
					time.sleep(1)
					state = state+1
				else:
					pass
			# This loop counts the switch flip with no delay so the motor can be stopped at the position.
			while state != diff:
				time.sleep(.15)
				value = controller.GPIODigitalGet(socket, 'GPIO4.DI')
				if value[0] != 0:
					XPSErrorHandler(controller,socket,value[0],'GPIODigitalGet')
				elif  int(format(value[1],"016b")[::-1][bit]) == val:
					state = state+1
				else:
					pass
			# Stopping the motor
			stop=x.GroupSpinModeStop(socket, group, 800)
			if stop[0] != 0:
				XPSErrorHandler(controller,socket,stop[0],'GroupSpinModeStop')
			# Checking to be sure the motor is in a valid position.
			elif int(format(value[1],"016b")[::-1][bit]) != val:		
				print 'motion failed, home and then reinitiate move'
			else:
				print 'motion succeded'
				Publisher().sendMessage((group+'_state'),state)
	else:
		pass


def NewportInitialize(controller,motor,socket,home_position):
	'''
An initialization function for any motor controlled by the XPS controller.

	Inputs: controller, motor, socket, home_position
	
	controller:	[xps]	Which instance of the XPS controller to use.
	wheel:		[str]	The name of the motor that is being used.  This is for config file purposes.
	socket:		[int]	Which socket to use to communicate with the XPS controller.
	current:	[int]	What position the motor is currently at.
	position:	[int]	What position the motor should move to.
	home:		[bool]	Determines whether the thread will find the home position or a different position.
'''
	GKill=controller.GroupKill(open_sockets[0], cfg[motor]['group'])	
	if GKill[0] != 0:
		XPSErrorHandler(open_sockets[0], GKill[0], 'GroupKill')
	GInit=controller.GroupInitialize(open_sockets[0], cfg[motor]['group'])
	if GInit[0] != 0:
		XPSErrorHandler(open_sockets[0], GInit[0], 'GroupInitialize')
	GHomeSearch=controller.GroupHomeSearchAndRelativeMove(open_sockets[0], cfg[motor]['group'],[home_position])
	print GHomeSearch
	if GHomeSearch[0] != 0:
		XPSErrorHandler(open_sockets[0], GHomeSearch[0], 'GroupHomeSearchAndRelativeMove')

if __name__ == '__main__':

	NewportInitialize(x,'grism',open_sockets[0],0)
	NewportWheelThread(x,'grism',open_sockets[0],1,4,True)
