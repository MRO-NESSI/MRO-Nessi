import wx

from focusREI import FocusREIPanel
from dewarwheelpanel import WheelPanel
from guideinfopanel import GuideInfoPanel
from kmirrorpanel import KmirrorPanel
from schematicpanel import SchematicPanel
from temppanel import TemperaturePanel

class OverviewPanel(wx.ScrolledWindow):
    """This panel provides control over most major
    actuators, as well as a temperature readout. Most
    operation can be carried out from this panel.
    """

    def __init__(self, parent, instrument):
        super(OverviewPanel, self).__init__(parent)
        
        self.SetScrollbars(20,20,55,40)
        
        # Attributes
        ################################################################
        self.Schematic   = SchematicPanel(self)
        self.Mask        = WheelPanel(self, 'mask', 
                                      instrument.mask_wheel)
        self.FilterOne   = WheelPanel(self, 'filter1', 
                                      instrument.filter1_wheel)
        self.FilterTwo   = WheelPanel(self, 'filter2', 
                                      instrument.filter2_wheel)
        self.Grism       = WheelPanel(self, 'grism', 
                                      instrument.grism_wheel)
        self.Kmirror     = KmirrorPanel(self, instrument.kmirror)
        self.GuideInfo   = GuideInfoPanel(self)
        self.FocusREI12  = FocusREIPanel(self, 'Focus Guide Cam',
                                         instrument.guide_focus)
        self.FocusREI34  = FocusREIPanel(self, 'Focus REI-3-4',
                                         instrument.REI34_focus)
        self.Temperature = TemperaturePanel(self, 
                                            instrument.temperature)
        
        self.__DoLayout()

    def __DoLayout(self):
        sbox = wx.StaticBox(self, label="")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)
        
        # Add controls to gridbag
        sizer.Add(self.Kmirror, pos=(0,0), span=(1,1), 
                  flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.FocusREI12, pos=(0,1), span=(1,1), 
                  flag=wx.LEFT|wx.ALIGN_BOTTOM)
        sizer.Add(self.GuideInfo, pos=(1,2), span=(1,1), 
                  flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.Schematic, pos=(1,0), span=(6,2), 
                  flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.FocusREI34, pos=(2,2), span=(1,1), 
                  flag=wx.LEFT|wx.ALIGN_BOTTOM)
        sizer.Add(self.Mask, pos=(3,2), span=(1,1), 
                  flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.FilterOne, pos=(4,2), span=(1,1), 
                  flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.FilterTwo, pos=(5,2), span=(1,1), 
                  flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.Grism, pos=(6,2), span=(1,1), 
                  flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.Temperature, pos=(0,2), span=(1,1), 
                  flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        # Add the grid bag to the static box and make everything fit
        boxSizer.Add(sizer, wx.EXPAND)
        self.SetSizerAndFit(boxSizer)


if __name__=='__main__':
    from instrument.instrument import Instrument
    import sys
    import os

    sys.path.append(os.path.expanduser('~/Documents/nessi/'))

    i = Instrument()

    app = wx.App()
    frame = OverviewPanel(None, i)
    frame.show()
