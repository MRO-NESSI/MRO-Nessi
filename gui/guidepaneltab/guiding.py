import numpy as np
import ds9
import wx

from guidecampanel import GuideCamPanel
from guidetemp import GuideTempPanel
from guidingpanel import GuidingPanel
from instrument.sensors.flicam import FLICam

class GuidePanel(wx.Panel):
    """Panel to interface with the guide camera."""

    def __init__(self, parent, instrument):
        """Build a GuidePanel.

        Arguments:
            parent     -- Parent panel.
            instrument -- Nessi instrument
        
        Raises:
            None
        """

        super(GuidePanel, self).__init__(parent)
        
        #Attributes
        ################################################################
        self.parent         = parent
        self.cam            = instrument.guide_cam
        self.instrument     = instrument

        #GUI Components
        ################################################################
        self.guideCamPanel  = GuideCamPanel(self)
        self.guideTempPanel = GuideTempPanel(self, self.cam)
        self.guidingPanel   = GuidingPanel(self)
        
        self.__DoLayout()

        #Start DS9 --- the image display
        ################################################################
        self.d = ds9.ds9()
        self.d.set("width 538")
        self.d.set("height 528")

        #Disable if the cam was not initialized
        ################################################################
        if self.cam is None:
            self.Enable(False)

    def __DoLayout(self):
        #Init sizers
        ################################################################
        #Outermost sizer
        mainSizer = wx.GridBagSizer(vgap=5, hgap=5)
        #Static box
        sbox      = wx.StaticBox(self, label="Guide Camera")
        #Sizer for static box
        boxSizer  = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        #Innermost sizer
        sizer     = wx.GridBagSizer(vgap=5, hgap=5)      
        
        #Add components to innermost sizer
        ################################################################
        sizer.Add(self.guideCamPanel, pos=(0,0), span=(1,3))
        sizer.Add(wx.StaticLine(self), pos=(1,0), span=(1,3), 
                  flag=wx.EXPAND|wx.BOTTOM)
        sizer.Add(self.guideTempPanel, pos=(2,0), span=(1,1))
        sizer.Add(wx.StaticLine(self, -1, style=wx.LI_VERTICAL),
                  pos=(2,1), span=(1,1), flag=wx.EXPAND)
        sizer.Add(self.guidingPanel, pos=(2,2), span=(1,1), 
                  flag=wx.EXPAND)
        
        #Add innermost sizer to static box sizer
        ################################################################
        boxSizer.Add(sizer)
        
        #Add static box sizer to outermost sizer
        ################################################################
        mainSizer.Add(boxSizer, pos=(0,0))

        #Set main sizer
        ################################################################
        self.SetSizer(mainSizer)

    def DisplayImage(self, image):
        """Displays a given image in ds9.
        
        Arguments:
            image -- a np2arr of the image.
        Raises:
            None
        """

        image[:] = np.fliplr(image)[:]
        self.d.set_np2arr(image)
        self.d.set("zoom to fit")
