import logging
from time import sleep

import wx

from overviewtab.overview   import OverviewPanel
from guidepaneltab.guiding  import GuidePanel
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
        self.nb = wx.Notebook(self.p, style=wx.NB_RIGHT)

        self.create_menus()

        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText("Welcome to NESSI!")

        
        #Make tabs
        ################################################################
        self.overviewPanel  = OverviewPanel(self.nb, self.instrument)
        self.guidingPanel   = GuidePanel(self.nb, self.instrument)
        self.settingsPanel  = SettingsPanel(self.nb, self.instrument)
        self.logPanel       = LogPanel(self.nb)
        self.emergencyPanel = EmergencyPanel(self.nb, self.instrument)

        #Add tabs to notebook
        ################################################################
        self.nb.AddPage(self.overviewPanel , "Overview")
        self.nb.AddPage(self.guidingPanel  , "Guiding")
        self.nb.AddPage(self.settingsPanel , "Settings")
        self.nb.AddPage(self.logPanel      , "Log")
        self.nb.AddPage(self.emergencyPanel, "Panic")

        #Place notebook panel into a sizer
        ################################################################
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.p.SetSizer(sizer)

        #Add an icon
        ################################################################
        self.SetIcon(wx.Icon('media/nessi.png', wx.BITMAP_TYPE_PNG))
        
        #Init statusbar logger
        ################################################################
        self.initStatusbarLogger()

        #Closeing handler
        ################################################################
        def OnClose(event):
            exit(0)

        self.Bind(wx.EVT_CLOSE, OnClose)


    def initStatusbarLogger(self, level=logging.INFO):
        """Sets up the logger to print to the status bar."""

        #LogEvent Callback
        ################################################################
        def onLogEvent(event):
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
