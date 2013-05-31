#!/usr/bin/env python
"""
 Control software for NESSI
 
 author:       Luke Schmidt, Matt Napolitano, Tyler Cecil
 author_email: lschmidt@nmt.edu
"""

__author__ = 'Luke Schmidt, Matt Napolitano, Tyler Cecil'
__date__ = '2013'

from configobj import ConfigObj
import logging
from logging.handlers import TimedRotatingFileHandler
from os import makedirs
from os.path import isdir
import sys
import time
import wx
from wx.lib.agw.advancedsplash import AdvancedSplash
from wx.lib.pubsub import Publisher as pub


from overviewtab.overview import OverviewPanel
from kmirrortab.kmirror import KMirrorPanel
from guidepaneltab.guiding import GuidingPanel
from settingstab.settings import SettingsPanel
from logtab.log import LogPanel, wxLogHandler, EVT_WX_LOG_EVENT
from emergencytab.emergency import EmergencyPanel
import actuators.XPS_C8_drivers as xps
from threadtools import timeout, TimeoutError


DEBUG = False

################# Master Dictionary for Instrument State #######################
keywords = {"OBSERVER"  : "Observer",
            "INST"      : "NESSI",
            "TELESCOP"  : "MRO 2.4m",
            "FILENAME"  : "default",
            "IMGTYPE"   : "imgtyp",
            "RA"        : "TCS down" ,   
            "DEC"       : "TCS down",  
            "AIRMASS"   : "TCS down",       
            "TELALT"    : "TCS down",
            "TELAZ"     : "TCS down",
            "TELFOCUS"  : "TCS down",
            "PA"        : "TCS down",
            "JD"        : "TCS down",
            "GDATE"     : "TCS down",
            "WINDVEL"   : "No Env data",
            "WINDGUST"  : "No Env data",
            "WINDDIR"   : "No Env data",
            "REI12"     : 0.0, # focus position
            "REI34"     : 0.0, # focus position
            "MASK"      : "None",
            "FILTER1"   : "None",
            "FILTER2"   : "None",
            "GRISM"     : "None",
            "EXP"       : 0.0,
            "CAMTEMP"   : 0.0,
            "CTYPE1"    : "RA---TAN",
            "CTYPE2"    : "DEC--TAN",
            "CRPIX1"    : 512.0,
            "CRPIX2"    : 512.0,
            "CDELT1"    : 0.0, 
            "CDELT2"    : 0.0,
            "CRVAL1"    : 0.0, 
            "CRVAL2"    : 0.0,
            "CROTA2"    : 0.0
            }

# General newport information to be passed to all relevant panels.
cfg = ConfigObj('nessisettings.ini')



                        
class MainNessiFrame(wx.Frame):
    """Main Window for Nessi Controll Software."""

    def __init__(self):
        wx.Frame.__init__(self, None, title="NESSI Controller", size=(850,875))

        #Make logfiles dir
        if not isdir('logfiles'): makedirs('logfiles')

        #Logger
        logging.basicConfig(level=logging.DEBUG)

        logTabFormatter = logging.Formatter('[%(asctime)s] %(filename)s:%(funcName)s - %(message)s')
        statusbarFormatter = logging.Formatter('[%(asctime)s] %(funcName)s - %(message)s')
        
        logfileHandler = logging.handlers.TimedRotatingFileHandler('logfiles/NESSILOG',
                                                                   when='d')
        logfileHandler.setLevel(logging.DEBUG)
        logfileHandler.setFormatter(logTabFormatter)
        logging.getLogger('').addHandler(logfileHandler)

        
        #add nessi package to path
        sys.path.append("./")

        self.x=xps.XPS()
        self.open_sockets=[]

        try:
            self.fill_socket_list(self.x)
        except TimeoutError:
            raise
            self.open_sockets=[0,1,2,3,4,5,6,7,8,9,10]
            logging.critical('Connection to the Newport controller failed.')   

        #Build Frame
        self.create_menus()
        self.statusbar=self.CreateStatusBar()
        
        #Init Notebook panel
        p = wx.Panel(self)
        nb = wx.Notebook(p, style=wx.NB_RIGHT)

        #Make tabs
        page1 = OverviewPanel(nb, self.x, self.open_sockets[1:])
#        page2 = KMirrorPanel(nb)
        page3 = GuidingPanel(nb)
        page4 = SettingsPanel(nb)
        page5 = LogPanel(nb)
        page6 = EmergencyPanel(nb, self.x, self.open_sockets[0], page1.FocusREI12.motor, page1.FocusREI34.motor)

        #Add tabs to notebook
        nb.AddPage(page1, "Overview")
#        nb.AddPage(page2, "K-Mirror")
        nb.AddPage(page3, "Guiding")
        nb.AddPage(page4, "Settings")
        nb.AddPage(page5, "Log")
        nb.AddPage(page6, "Panic")

        # Add icon
        path = "media/nessi.png"
        icon = wx.Icon(path, wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)
        
        #Place notebook panel into a sizer
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)

        #init status
        self.statusbar.SetStatusText("Welcome to NESSI!")

        #Make logfiles dir
        if not isdir('logfiles'): makedirs('logfiles')

        #Logger GUI Handlers
        logTabHandler = wxLogHandler(page5)
        logTabHandler.setFormatter(logTabFormatter)
        logTabHandler.setLevel(logging.INFO)
        logging.getLogger('').addHandler(logTabHandler)

        statusbarHandler = wxLogHandler(self)
        statusbarHandler.setFormatter(statusbarFormatter)
        statusbarHandler.setLevel(logging.INFO)
        logging.getLogger('').addHandler(statusbarHandler)

        self.Bind(EVT_WX_LOG_EVENT, self.onLogEvent)

        logging.info('NESSI initialized.')

    def onLogEvent(self, event):
        msg = event.message.strip('\r') + '\n'
        self.statusbar.SetStatusText(msg)
        event.Skip()
        
    def create_menus(self):
        menuBar = wx.MenuBar()

        # Attributes
        FileMenu = wx.Menu()
        about_item   = FileMenu.Append(wx.ID_ABOUT, text="&About NESSI Controller")
        quit_item    = FileMenu.Append(wx.ID_EXIT, text="&Quit")
        
        # Event Handlers
        self.Bind(wx.EVT_MENU, self.OnAbout, about_item)
        self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
        
        menuBar.Append(FileMenu, "&File")
        self.SetMenuBar(menuBar)

    def OnQuit(self, event=None):
        close_sockets()
        self.Close()
        
    def OnAbout(self, event=None):
        info = wx.AboutDialogInfo()
        info.SetName('NESSI Controller')
        info.SetVersion('0.1')
        info.SetDescription('NESSI Controller is an interface to the New Mexico Tech Extrasolar Spectroscopic Survey Instrument. Email lschmidt@nmt.edu with questions.')
        info.SetCopyright('(C) 2013 Luke Schmidt, Matt Napolitano, Tyler Cecil, NMT/MRO')

        wx.AboutBox(info)

    @timeout(10)
    def fill_socket_list(self, controller):
        for i in range(int(cfg['general']['sockets'])):
            self.open_sockets.append(controller.TCP_ConnectToServer('192.168.0.254',5001,1))
        
        # Checking the status of the connections.
        for i in range(int(cfg['general']['sockets'])):
            if self.open_sockets[i] == -1:
                logging.critical('Newport socket connection not opened at position ' + str(i))
                break
            else:
                pass
    
    @timeout(10)
    def close_sockets(self, controller):
        for i in range(len(self.open_sockets)):
            controller.TCP_CloseSocket(self.open_sockets[i])

if __name__ == "__main__":
    app = wx.App()
    #################MAKE SPALSH################
    bitmap = wx.Bitmap("media/nessi-logo.png", wx.BITMAP_TYPE_PNG)
    splash = AdvancedSplash(None, bitmap=bitmap)
    splash.SetText('TEST!')
    
    ################START LOGGER################
    def onLogEvent(self, event):
        msg = event.message.strip('\r') + '\n'
        print 'I WAS CALLED %s' % msg
        wx.CallAfter(splash.SetText,msg)
        wx.Yield()
        event.Skip()

    #Logger
    logging.basicConfig(level=logging.DEBUG)

    splashHandler = wxLogHandler(splash)
    splashHandler.setLevel(logging.INFO)
    logging.getLogger('').addHandler(splashHandler)

    splash.Bind(EVT_WX_LOG_EVENT, onLogEvent)
    
    logging.info('This is a test')
    ################Main Frame################
    main = MainNessiFrame()
    logging.getLogger('').removeHandler(splashHandler)
    splash.Destroy() #Kill splash
    main.Show()
    ################RUN################
    app.MainLoop()
