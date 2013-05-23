import prefcontrol
import wx


class SettingsPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super(SettingsPanel, self).__init__(parent)
        
        # Attributes
                
        self.scopeLbl = wx.StaticText(self, wx.ID_ANY, "Telescope Server:")
        self.scopeTxt = wx.TextCtrl(self, wx.ID_ANY, "")
        self.scopeTxt.Disable()
 
        self.scopeportLbl = wx.StaticText(self, wx.ID_ANY, "Telescope Port:")
        self.scopeportTxt = wx.TextCtrl(self, wx.ID_ANY, "")
        self.scopeportTxt.Disable()
 
        self.savefolderLbl = wx.StaticText(self, wx.ID_ANY, "Save Folder:")
        self.savefolderTxt = wx.TextCtrl(self, wx.ID_ANY, "")
        self.savefolderTxt.Disable()
 
        self.instportLbl = wx.StaticText(self, wx.ID_ANY, "Instrument Port:")
        self.instportTxt = wx.TextCtrl(self, wx.ID_ANY, "")
        self.instportTxt.Disable()
        
        self.pixelscalexLbl = wx.StaticText(self, wx.ID_ANY, "Guide Camera Pixel Scale X (deg/pixel):")
        self.pixelscalexTxt = wx.TextCtrl(self, wx.ID_ANY, "")
        self.pixelscalexTxt.Disable()
        
        self.pixelscaleyLbl = wx.StaticText(self, wx.ID_ANY, "Guide Camera Pixel Scale Y (deg/pixel):")
        self.pixelscaleyTxt = wx.TextCtrl(self, wx.ID_ANY, "")
        self.pixelscaleyTxt.Disable()
        
        self.observerLbl = wx.StaticText(self, wx.ID_ANY, "Observer:")
        self.observerTxt = wx.TextCtrl(self, wx.ID_ANY, "")
        self.observerTxt.Disable()
        
        self.editbtn = wx.Button(self, label="Edit")
        self.editadvbtn = wx.Button(self, label="Advanced")
        self.savebtn = wx.Button(self, label="Save")
        
        self.widgets = [self.savefolderTxt, self.instportTxt, self.pixelscalexTxt, self.pixelscaleyTxt, self.observerTxt]
        self.advwidgets = [self.scopeTxt, self.scopeportTxt, self.savefolderTxt, self.instportTxt, self.pixelscalexTxt, self.pixelscaleyTxt, self.observerTxt]
        
        # Layout
        self.__DoLayout()

        # Handlers
        self.Bind(wx.EVT_BUTTON, self.editPreferences, self.editbtn)
        self.Bind(wx.EVT_BUTTON, self.editAdvPreferences, self.editadvbtn)
        self.Bind(wx.EVT_BUTTON, self.savePreferences, self.savebtn)
   
    def __DoLayout(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        prefSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        prefSizer.AddGrowableCol(1)
 
        prefSizer.Add(self.scopeLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.scopeTxt, 0, wx.EXPAND)
        prefSizer.Add(self.scopeportLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.scopeportTxt, 0, wx.EXPAND)
        prefSizer.Add(self.savefolderLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.savefolderTxt, 0, wx.EXPAND)
        prefSizer.Add(self.instportLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.instportTxt, 0, wx.EXPAND)
        prefSizer.Add(self.pixelscalexLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.pixelscalexTxt, 0, wx.EXPAND)
        prefSizer.Add(self.pixelscaleyLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.pixelscaleyTxt, 0, wx.EXPAND)
        prefSizer.Add(self.observerLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.observerTxt, 0, wx.EXPAND)
        prefSizer.Add(self.editbtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.savebtn, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        prefSizer.Add(self.editadvbtn, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
                
        mainSizer.Add(prefSizer, 0, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizer(mainSizer)
 
        # ---------------------------------------------------------------------
        # load preferences
        self.loadPreferences()
 
    #----------------------------------------------------------------------
    def loadPreferences(self):
        """
        Load the preferences and fill the text controls
        """
        config = prefcontrol.getConfig()
        scope = config['scope server']
        scopeport = config['scope port']
        savefolder = config['savefolder']
        instport = config['instrument port']
        pixelscalex = config['pixel scale x']
        pixelscaley = config['pixel scale y']
        observer = config['Observer']
 
        self.scopeTxt.SetValue(scope)
        self.scopeportTxt.SetValue(scopeport)
        self.savefolderTxt.SetValue(savefolder)
        self.instportTxt.SetValue(instport)
        self.pixelscalexTxt.SetValue(pixelscalex)
        self.pixelscaleyTxt.SetValue(pixelscaley)
        self.observerTxt.SetValue(observer)
 
    #----------------------------------------------------------------------
    def editPreferences(self, event):
        """Allow a user to edit the preferences"""
        for widget in self.widgets:
            widget.Enable()
            
    #----------------------------------------------------------------------
    def editAdvPreferences(self, event):
        """Allow an admin to edit the preferences"""
        for widget in self.advwidgets:
            widget.Enable()        
        
    #----------------------------------------------------------------------
    def savePreferences(self, event):
        """
        Save the preferences
        """
        config = prefcontrol.getConfig()
 
        config['scope server'] = str(self.scopeTxt.GetValue())
        config['scope port'] = self.scopeportTxt.GetValue()
        config['savefolder'] = str(self.savefolderTxt.GetValue())
        config['instrument port'] = self.instportTxt.GetValue()
        config['pixel scale x'] = self.pixelscalexTxt.GetValue()
        config['pixel scale y'] = self.pixelscaleyTxt.GetValue()
        config['Observer'] = self.observerTxt.GetValue()
                
        config.write()

        for widget in self.advwidgets:
            widget.Disable() 
 
        dlg = wx.MessageDialog(self, "Preferences Saved!", 'Information',  
                               wx.OK|wx.ICON_INFORMATION)
        dlg.ShowModal()        
