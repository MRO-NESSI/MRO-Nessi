import wx

class KMirrorPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super(KMirrorPanel, self).__init__(parent)
        
        # Attributes
        self.t = wx.StaticText(self, -1, "K-Mirror Control", (40,40))

        self.__DoLayout()

    def __DoLayout(self):
        sbox = wx.StaticBox(self, label="")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)
        
        # Add controls to gridbag
        sizer.Add(self.t, pos=(0,0), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
                
        # Add the grid bag to the static box and make everything fit
        boxSizer.Add(sizer, wx.EXPAND)
        self.SetSizerAndFit(boxSizer)
