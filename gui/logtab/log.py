import logging
import time
import wx
import wx.lib.newevent
from wx.richtext import RichTextCtrl

# create event type
wxLogEvent, EVT_WX_LOG_EVENT = wx.lib.newevent.NewEvent()


class wxLogHandler(logging.Handler):
    """
    A handler class which sends log strings to a wx object
    """
    def __init__(self, wxDest=None):
        """
        Initialize the handler
        @param wxDest: the destination object to post the event to 
        @type wxDest: wx.Window
        """
        logging.Handler.__init__(self)
        self.wxDest = wxDest
        self.level = logging.DEBUG


    def flush(self):
        """
        does nothing for this handler
        """


    def emit(self, record):
        """
        Emit a record.
        """
        try:
            msg = self.format(record)
            evt = wxLogEvent(message=msg,levelname=record.levelname)            
            wx.PostEvent(self.wxDest,evt)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class LogPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super(LogPanel, self).__init__(parent)

        # Attributes
        self.logTxt = wx.StaticText(self, wx.ID_ANY, "Instrument Log:")
        self.log = RichTextCtrl(self, -1, size=(-1,130), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.log.SetBackgroundColour('#B0D6B0')
        self.obs_logTxt = wx.StaticText(self, wx.ID_ANY, "Observing Comments:")
        self.obs_log = wx.TextCtrl(self, -1, size=(-1,75), style=wx.TE_MULTILINE)
        self.log_button = wx.Button(self, label="Log")
        self.log_button.Bind(wx.EVT_BUTTON, self.onLog)
        
        self.guidelogTxt = wx.StaticText(self, wx.ID_ANY, "Guiding Log:")
        self.guidelog = wx.TextCtrl(self, -1, size=(-1,130), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.guidelog.SetBackgroundColour('#B0D6B0')

        # Layout       
        self.__DoLayout()

        #Taken from http://wiki.wxpython.org/StyledTextCtrl%20Log%20Window%20Demo
        self.log._styles = [None]*32
        self.log._free = 1

        #EVT_WX_LOG_EVENT
        self.Bind(EVT_WX_LOG_EVENT, self.onLogEvent)
        
    def __DoLayout(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        instSizer = wx.BoxSizer(wx.VERTICAL)
        
        guideSizer = wx.FlexGridSizer(cols=1, hgap=5, vgap=5)
        guideSizer.AddGrowableCol(0)
        guideSizer.AddGrowableRow(0)
        
        instSizer.Add(self.logTxt, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        instSizer.Add(self.log, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        instSizer.Add(self.obs_logTxt, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        instSizer.Add(self.obs_log, 0, wx.EXPAND)
        instSizer.Add(self.log_button, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
                    
        guideSizer.Add(self.guidelogTxt, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        guideSizer.Add(self.guidelog, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)            
                        
        mainSizer.Add(instSizer, 1, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(guideSizer, 0, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(mainSizer)

    
    def onLog(self, event):
        msg = 'OBSERVER: ' + self.obs_log.GetValue()
        logging.info(msg)
        self.obs_log.SetValue('')

    def onLogEvent(self, event):
        colors = {
            'DEBUG'    :'black',
            'INFO'     :'black',
            'WARNING'  :'yellow',
            'ERROR'    :'red',
            'CRITICAL' : 'red'
            }
        msg = event.message.strip('\r') + '\n'
        self.log.SetInsertionPointEnd()
        self.log.BeginTextColour(colors[event.levelname])
        self.log.WriteText(msg)
        self.log.EndTextColour()
        event.Skip()
