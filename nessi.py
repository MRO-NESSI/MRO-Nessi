#!/usr/bin/env python
"""
 Control software for NESSI
 
 author:       Luke Schmidt, Matt Napolitano, Tyler Cecil
 author_email: lschmidt@nmt.edu
"""

__author__ = 'Luke Schmidt, Matt Napolitano, Tyler Cecil'
__date__ = '2013'

import sys
import time
import wx
from wx.lib.pubsub import Publisher as pub

from overviewtab.overview import OverviewPanel
from kmirrortab.kmirror import KMirrorPanel
from guidepaneltab.guiding import GuidingPanel
from settingstab.settings import SettingsPanel
from logtab.log import LogPanel
from emergency import EmergencyPanel

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
                        
class MainNessiFrame(wx.Frame):
    """Main Window for Nessi Controll Software."""

    def __init__(self):
        wx.Frame.__init__(self, None, title="NESSI Controller", size=(850,875))
        
        #add nessi package to path
        sys.path.append("./")

        #Build Frame
        self.create_menus()
        self.statusbar=self.CreateStatusBar()
        
        #Init Notebook panel
        p = wx.Panel(self)
        nb = wx.Notebook(p, style=wx.NB_RIGHT)

        #Make tabs
        page1 = OverviewPanel(nb)
        page2 = KMirrorPanel(nb)
        page3 = GuidingPanel(nb)
        page4 = SettingsPanel(nb)
        page5 = LogPanel(nb)
        #page6 = EmergencyPanel(nb)

        #Add tabs to notebook
        nb.AddPage(page1, "Overview")
        nb.AddPage(page2, "K-Mirror")
        nb.AddPage(page3, "Guiding")
        nb.AddPage(page4, "Settings")
        nb.AddPage(page5, "Log")
        #nb.AddPage(page6, "Panic")

        # Add icon
        path = "media/nessi.png"
        icon = wx.Icon(path, wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)
        
        pub.subscribe(self.change_statusbar, 'change_statusbar')
        
        #Place notebook panel into a sizer
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)

        self.statusbar.SetStatusText("Welcome to NESSI!")

    def change_statusbar(self, msg):
        print msg.data
        self.statusbar.SetStatusText(msg.data)
        
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
        self.Close()
        
    def OnAbout(self, event=None):
        info = wx.AboutDialogInfo()
        info.SetName('NESSI Controller')
        info.SetVersion('0.1')
        info.SetDescription('NESSI Controller is an interface to the New Mexico Tech Extrasolar Spectroscopic Survey Instrument. Email lschmidt@nmt.edu with questions.')
        info.SetCopyright('(C) 2013 Luke Schmidt, Matt Napolitano, Tyler Cecil, NMT/MRO')

        wx.AboutBox(info)

if __name__ == "__main__":
    app = wx.App()
    MainNessiFrame().Show()
    app.MainLoop()
