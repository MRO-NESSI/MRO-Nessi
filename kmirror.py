#!/usr/bin/env python

# kmirror.py
# Matt Napolitano
# Created: 01/18/2012

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
'''
The K-Mirror testing app.
'''	
	def OnInit(self):
		self.frame=KMirrorFrame(None, title='K-Mirror Testing Program')
		self.SetTopWindow(self.frame)
		self.frame.Show()
		return True

class KMirrorFrame(wx.Frame):
'''
The frame for the K-Mirror panel.
'''
	def __init__(self,*args,**kwargs):
		super(KMirrorFrame,self).__init__(*args,**kwargs)
		

