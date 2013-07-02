import logging

import wx

from overviewtab.overview   import OverviewPanel
from kmirrortab.kmirror     import KMirrorPanel
from guidepaneltab.guiding  import GuidingPanel
from settingstab.settings   import SettingsPanel
from logtab.log             import LogPanel, wxLogHandler, EVT_WX_LOG_EVENT
from emergencytab.emergency import EmergencyPanel

class MainNessiFrame(wx.Frame):
    """Main Window for Nessi Control Software."""

    def __init__(self, instrument):
        wx.Frame.__init__(self, None, title="NESSI Controller", 
                          size=(850,875))
        
        self.instrument = instrument

        #Build Frame
        ################################################################
        self.p  = wx.Panel(self)
        self.nb = wx.Notebook(p, style=wx.NB_RIGHT)

        self.create_menus()

        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText("Welcome to NESSI!")

        
        #Make tabs
        ################################################################
        self.overviewPanel  = OverviewPanel(self.nb, self.instrument)
        self.guidingPanel   = GuidingPanel(nb)
        self.settingsPanel  = SettingsPanel(nb)
        self.logPanel       = LogPanel(nb)
        self.emergencyPanel = EmergencyPanel(nb, self.x, 
                                             self.open_sockets[0], 
                                             page1.FocusREI12.motor, 
                                             page1.FocusREI34.motor)

        #Add tabs to notebook
        ################################################################
        nb.AddPage(self.overviewPanel , "Overview")
        nb.AddPage(self.guidingPanel  , "Guiding")
        nb.AddPage(self.settingsPanel , "Settings")
        nb.AddPage(self.logPanel      , "Log")
        nb.AddPage(self.emergencyPanel, "Panic")

        #Place notebook panel into a sizer
        ################################################################
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)

        #Add an icon
        ################################################################
        self.SetIcon(wx.Icon('media/nessi.png', wx.BITMAP_TYPE_PNG))
        
        #Init statusbar logger
        ################################################################
        self.initStatusbarLogger()


    def initStatusbarLogger(self, level=logging.INFO):
        """Sets up the logger to print to the status bar."""

        #LogEvent Callback
        ################################################################
        def onLogEvent(self, event):
            msg = event.message.strip('\r') + '\n'
            self.statusbar.SetStatusText(msg)
            event.Skip()

        #Init formatter
        ################################################################
        statusbarFormatter = logging.Formatter(
            '[%(asctime)s] %(funcName)s - %(message)s')

        #Init handler
        ################################################################
        statusbarHandler = wxLogHandler(self)
        statusbarHandler.setFormatter(statusbarFormatter)
        statusbarHandler.setLevel(level=level)
        logging.getLogger('').addHandler(statusbarHandler)

        self.Bind(EVT_WX_LOG_EVENT, onLogEvent)

        
    def create_menus(self):
        """Builds the menu bar, and attaches."""

        #Build menu lists
        ################################################################
        menuBar  = wx.MenuBar()
        FileMenu = wx.Menu()

        #File Menu List
        ################################################################
        about_item = FileMenu.Append(wx.ID_ABOUT, 
                                     text="&About NESSI Controller")
        quit_item  = FileMenu.Append(wx.ID_EXIT, text="&Quit")

        # Event Handlers
        ################################################################
        self.Bind(wx.EVT_MENU, self.OnAbout, about_item)
        self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
        
        #Add menu lists and add menu bar.
        ################################################################
        menuBar.Append(FileMenu, "&File")
        self.SetMenuBar(menuBar)

    def OnQuit(self, event):
        """Bound to File Menu."""
        self.Close()
        
    def OnAbout(self, event):
        """Make an about box for our software.

        Bound in the File Menu.
        """
        info = wx.AboutDialogInfo()
        info.SetName('NESSI Controller')
        #TODO: integrate this with git?
        info.SetVersion('0.8')
        info.SetDescription('NESSI Controller is an interface to the'
                            ' New Mexico Tech Extrasolar Spectroscopic'
                            ' Survey Instrument. Email lschmidt@nmt.edu'
                            ' with questions.')
        info.SetCopyright(  '(C) 2013 Luke Schmidt, Matt Napolitano,'
                            ' Tyler Cecil, NMT/MRO')
        wx.AboutBox(info)

"""
        #Logger GUI Handlers
        logTabFormatter = logging.Formatter(
            '[%(asctime)s] %(filename)s:%(funcName)s - %(message)s')
        logTabHandler = wxLogHandler(page5)
        logTabHandler.setFormatter(logTabFormatter)
        logTabHandler.setLevel(logging.INFO)
        logging.getLogger('').addHandler(logTabHandler)

        logging.info('NESSI initialized.')
"""
