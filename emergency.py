import wx
from actuators.newport import XPSErrorHandler

class EmergencyPanel(wx.Panel):
    def __init__(self, parent, controller, socket, thorlabs1, thorlabs2, *args, **kwargs):
        super(EmergencyPanel, self).__init__(parent)
        
        self.controller = controller
        self.socket = socket
        self.thorlabs1 = thorlabs1
        self.thorlabs2 = thorlabs2
        # Attributes
        self.t = wx.StaticText(self, -1, "Emergency", (40,40))
        self.emergency = wx.Button(self,label='KILL ALL', size=(400,200))
        self.emergency.SetBackgroundColour(wx.Colour(255,0, 0))
        self.emergency.ClearBackground()
        self.emergency.Refresh() 
        self.font=wx.Font(pointSize = 40, family = wx.FONTFAMILY_DECORATIVE, style = wx.FONTSTYLE_NORMAL, weight = wx.FONTWEIGHT_BOLD)
        self.emergency.SetFont(self.font)  
        self.Bind(wx.EVT_BUTTON,self.OnButton)

        self.__DoLayout()

    def __DoLayout(self):
        sbox = wx.StaticBox(self, label="")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)
        
        # Add controls to gridbag
        sizer.Add(self.t, pos=(0,0), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.emergency, pos=(1,0),span=(1,1), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.CENTER)
                
        # Add the grid bag to the static box and make everything fit
        boxSizer.Add(sizer, wx.EXPAND|wx.CENTER)
        self.SetSizerAndFit(boxSizer)

    def OnButton(self, event):
        kill=self.controller.KillAll(self.socket)
        # This checks to insure the kill command worked.  If it did not work, the standard error handler is called.
        if kill[0] != 0:
            XPSErrorHandler(self.controller, self.socket, kill[0], 'KillAll')
        self.thorlabs1.home()
        self.thorlabs2.home()
        pass
