import wx

from guidepanelsettings import GuidePanelSettings

class GuidingPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super(GuidingPanel, self).__init__(parent)
        
        # Attributes
        self.Guide = GuidePanelSettings(self)
        self.parent = parent        
        self.__DoLayout()

    def __DoLayout(self):
        ## Layout for this panel:
        ##
        ##    0               1
        ##   +---------------+---------------+
        ## 0 | k-mirror      | guiding       |
        ##   +---------------+---------------+
        ## 1 | schematic     | self.new_dec  |
        ##   +---------------+---------------+
        ##
        sbox = wx.StaticBox(self, label="")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)
        
        # Add controls to gridbag
        sizer.Add(self.Guide, pos=(0,0), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
                
        # Add the grid bag to the static box and make everything fit
        boxSizer.Add(sizer, wx.EXPAND)
        self.SetSizerAndFit(boxSizer)
