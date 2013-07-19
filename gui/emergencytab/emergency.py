import wx

class EmergencyPanel(wx.Panel):
    """This panel contains a single button, which may
    be used to kill the instrument. 
    """

    def __init__(self, parent, instrument):
        super(EmergencyPanel, self).__init__(parent)

        self.instrument = instrument

        #GUI Components
        ################################################################
        self.label     = wx.StaticText(self, -1, "Emergency", (40,40))
        self.emergency = wx.Button(self, 1, label='KILL ALL', 
                                   size=(400,200))

        self.emergency.SetBackgroundColour(wx.Colour(255,0, 0))
        self.emergency.ClearBackground()
        self.emergency.Refresh() 

        font = wx.Font(pointSize = 40, 
                       family = wx.FONTFAMILY_DECORATIVE, 
                       style = wx.FONTSTYLE_NORMAL, 
                       weight = wx.FONTWEIGHT_BOLD)
        self.emergency.SetFont(font)  
        self.Bind(wx.EVT_BUTTON, self.OnEmergency, id = 1)

        self.__DoLayout()

    def __DoLayout(self):
        sbox     = wx.StaticBox(self, label="")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer    = wx.GridBagSizer(vgap=2, hgap=2)
        
        #Add controls to gridbag
        ################################################################
        sizer.Add(self.label, pos=(0,0), span=(1,1), 
                  flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.emergency, pos=(1,0),span=(1,1), 
                  flag=wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
                
        #Add the grid bag to the static box and make everything fit
        ################################################################
        boxSizer.Add(sizer, wx.EXPAND|wx.CENTER)
        self.SetSizerAndFit(boxSizer)

    def OnEmergency(self, event):
        #TODO: Ask the user what to do next.
        self.instrument.kill_all()
