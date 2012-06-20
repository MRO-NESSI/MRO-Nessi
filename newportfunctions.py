#!/usr/bin/env python

# newportfunctions.py
# Matt Napolitano
# Created 06/19/2012

# This is designed to be a module used by the NESSI GUI to interact with the newport controller.

import wx
import XPS_C8_drivers as xps
import wx.lib.pubsub as pub
#import nessilogging as log

# Initializing the controller
x = xps.XPS()

# Initializing a list of socket IDs.  This will be empty until the Initialize function is called.
socketid = []

# The general error handing function for the newport controller.
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


# The initialization function to open sockets to the controller.
def InitializeSockets(numberofsockets):
	'''Open a specified number of sockets to the newport controller.  
	The number of sockets should be an integer less than 100.
	'''
	# The counter for a while loop, starting a zero.
	count = 0
	# Reinitializing the list to be sure it is free of clutter from previous uses of the function. 
	socketid = []
	# Checking the input for the function. 
	if type(numberofsockets) == int:
		# The while loop that opens the sockets.  The termination conditions also make sure users cannot try to open more sockets than the controller can handle.
		while count < numberofsockets and count < 100:
			# This adds the new socket to the end of the list of sockets.
			socketid.append(x.TCP_ConnectToServer('192.168.0.254',5001,1))
			# This checks to be sure the socket opened. If not, it takes appropriate measures.
			if socketid[count] == -1:
				print 'Connection to Newport Controller has failed.\nPlease Check IP and Port.'
				#log.Logger(stuff)				
				#sys.exit()
				
			else:
				count += 1	
				#log.logger(stuff)
		# Temp code to inform the user of succes.
		print str(count) + ' sockets opened.'

	# Handling improper input.
	else:
		print 'Type Error: number of sockets must be an integer. No sockets initialized.'

# The close function terminates all connection to the controller.
def Close():
	'''Recursively close all connections to the newport controller.'''
	# Initializing the count for the loop.
	count = 0
	# The while loop that recursively closes all the connections to the controller.
	while count < len(socketid):
		x.TCP_CloseSocket(socketid[count])
		count += 1

# This function will poll the controller for some parameter value and send it to a publisher location.
def Track(socket,group,positioner,parameter,location):
	'''Poll the controller for a parameter value about one of the motors.
	Verify the data is recieved.
	Send the returned value to a publisher location.
	
	Parameter definitions:
		0: 
		1:
		2:
	'''
	if parameter == 0:
		result=x.stuff()
		if result[0] != 0:
			XPSErrorHandler(socket,result[0],name):
		else:
			pub.Publisher().sendMessage((str(location)),result[1])
	
	elif parameter == 1:
		pass

	else:
		pass

# This function will control the movement of the motors.
def Move(socket,group,positioner,movetype,movement):
	'''Move the specified motor given the specified parameters from the movement input. '''
	if movetype == 0:
		pass

	elif movetype == 1:
		pass

	else:
		pass
		
#The emergency kill function.
def Emergency():
	'''Send the kill all command to the controller. '''
	kill=x.KillAll(socketid[0])
	# This checks to insure the kill command worked.  If it did not work, the standard error handler is called.
	if kill[0] != 0:
		XPSErrorHandler(SocketID, kill[0], 'KillAll')
	# If the command worked, a message is displayed telling the user that it was succesful and that the groups need to be reinitialized before they can be used again.
	else:
		result=wx.MessageBox('All Groups Killed.\nGroups Must Be Reinitialized.',style=wx.CENTER|wx.ICON_EXCLAMATION|wx.OK)	
		
