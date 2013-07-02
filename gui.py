import logging

import wx

from overviewtab.overview import OverviewPanel
from kmirrortab.kmirror import KMirrorPanel
from guidepaneltab.guiding import GuidingPanel
from settingstab.settings import SettingsPanel
from logtab.log import LogPanel, wxLogHandler, EVT_WX_LOG_EVENT
from emergencytab.emergency import EmergencyPanel


class MainNessiFrame(wx.Frame):
    """Main Window for Nessi Controll Software."""

    def __init__(self):
        wx.Frame.__init__(self, None, title="NESSI Controller", 
                          size=(850,875))

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
        logTabFormatter = logging.Formatter(
            '[%(asctime)s] %(filename)s:%(funcName)s - %(message)s')
        statusbarFormatter = logging.Formatter(
            '[%(asctime)s] %(funcName)s - %(message)s')
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
