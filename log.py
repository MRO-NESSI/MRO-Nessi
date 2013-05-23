import wx

class LogPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super(LogPanel, self).__init__(parent)
        
        # Attributes
        self.logTxt = wx.StaticText(self, wx.ID_ANY, "Instrument Log:")
        self.log = wx.TextCtrl(self, -1, size=(-1,130), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.log.SetBackgroundColour('#B0D6B0')
        self.obs_logTxt = wx.StaticText(self, wx.ID_ANY, "Observing Comments:")
        self.obs_log = wx.TextCtrl(self, -1, size=(-1,75), style=wx.TE_MULTILINE)
        self.log_button = wx.Button(self, label="Log")
        
        self.guidelogTxt = wx.StaticText(self, wx.ID_ANY, "Guiding Log:")
        self.guidelog = wx.TextCtrl(self, -1, size=(-1,130), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.guidelog.SetBackgroundColour('#B0D6B0')
        # Layout       
        self.__DoLayout()

    def __DoLayout(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        instSizer = wx.FlexGridSizer(cols=1, hgap=5, vgap=5)
        instSizer.AddGrowableCol(0)
        
        guideSizer = wx.FlexGridSizer(cols=1, hgap=5, vgap=5)
        guideSizer.AddGrowableCol(0)
        
        instSizer.Add(self.logTxt, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        instSizer.Add(self.log, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        instSizer.Add(self.obs_logTxt, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        instSizer.Add(self.obs_log, 0, wx.EXPAND)
        instSizer.Add(self.log_button, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
                    
        guideSizer.Add(self.guidelogTxt, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        guideSizer.Add(self.guidelog, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)            
                        
        mainSizer.Add(instSizer, 0, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(guideSizer, 0, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(mainSizer)

    def open_log(self):
        logtime = time.strftime("%a%d%b%Y-%H:%M:%S", time.gmtime())
        loggerfile = settings.save_folder+logtime+".log"
        self.logfile = open(loggerfile, 'a')
        self.logfile.write('Starting up ' + logtime + '\n')
    
    def close_log(self):
        log.close()
        
    def on_log_button(self, event):
        localtime = time.asctime(time.gmtime())
        note = self.obs_log.GetValue()
        self.log.AppendText(str(datetime.utcnow()) + '\n        ' + note + '\n\n')
        self.write_log(str(datetime.utcnow()) + '  ' + note)
        wx.TextCtrl.Clear(self.obs_log)
        
    def log_evt(self, msg):
        self.log.AppendText(str(datetime.utcnow()) + '\n        ' + msg.data + '\n')
        self.write_log(str(datetime.utcnow()) + '  ' + msg.data)
        self.parent.SetStatusText(msg.data)
    
    
    def write_log(self, note):
        #insert newline every 80 characters
        nlnote = self.insert_newlines(note)
        self.logfile.write('\n' + nlnote + '\n')

    def insert_newlines(self, string):
        dedented_text = textwrap.dedent(string).strip()
        return textwrap.fill(dedented_text, initial_indent='', subsequent_indent='    ', width=80)

