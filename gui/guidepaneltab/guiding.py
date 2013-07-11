import numpy as np
import logging
import ds9
import wx

from guidecampanel import GuideCamPanel
from guidetemp import GuideTempPanel
from guidingpanel import GuidingPanel
from sensors.flicam import FLICam

class GuidePanelSettings(wx.Panel):
    """Panel to interface with the guide camera."""
    """TODO: It shouldn't be settings..."""

    def __init__(self, parent, *args, **kwargs):
        super(GuidePanelSettings, self).__init__(parent)
        
        self.parent         = parent
        self.cam            = FLICam()
        self.guideCamPanel  = GuideCamPanel(self)
        self.guideTempPanel = GuideTempPanel(self)
        self.guidingPanel   = GuidingPanel(self)
        
        self.__DoLayout()

        # Start up image display
        self.d = ds9.ds9()
        self.d.set("width 538")
        self.d.set("height 528")

    def __DoLayout(self):
        # Set up master StaticBox
        sbox = wx.StaticBox(self, label="Guide Camera")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=5, hgap=5)      
        
        # add sizers to master sizer
        sizer.Add(self.guideCamPanel,       pos=(0,0), span=(1,3))
        sizer.Add(wx.StaticLine(self),   pos=(1,0), span=(1,3), flag=wx.EXPAND|wx.BOTTOM)
        sizer.Add(self.guideTempPanel,      pos=(2,0), span=(1,1))
        sizer.Add(wx.StaticLine(self, -1, style=wx.LI_VERTICAL),   pos=(2,1), span=(1,1), flag=wx.EXPAND)
        sizer.Add(self.guidingPanel,     pos=(2,2), span=(1,1), flag=wx.EXPAND)
        
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizerAndFit(boxSizer)

    def DisplayImage(self, image):
        image[:] = np.fliplr(image)[:]
        self.d.set_np2arr(image)
        self.d.set("zoom to fit")
