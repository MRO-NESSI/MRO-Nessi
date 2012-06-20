#!/usr/bin/env python

# newportfunctions.py
# Matt Napolitano
# Created 06/19/2012

# This is designed to be a module used by the NESSI GUI to interact with the newport controller.

import XPS_C8_drivers as xps
#import nessilogging as log

# Initializing the controller
x = xps.XPS()

# Initializing a list of socket IDs.  This will be empty until the Initialize function is called.
socketid = []

# The initialization function to open sockets to the controller.
def Initialize(numberofsockets):
	'''This function will open a specified number of sockets to the newport controller.  The number of sockets must be an integer less than 100.'''
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
	'''This function will recursively close all connections to the newport controller.'''
	# Initializing the count for the loop.
	count = 0
	# The while loop that recursively closes all the connections to the controller.
	while count < len(socketid):
		x.TCP_CloseSocket(socketid[count])
		count += 1
