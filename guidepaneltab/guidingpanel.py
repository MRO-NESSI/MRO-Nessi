import wx

class GuidingPanel(wx.Panel):
    
    def __init__(self, parent):
        super(GuidingPanel, self).__init__(parent)

        self.star1 = wx.StaticText(self, label="Star 1: ")
        self.star2 = wx.StaticText(self, label="Star 2: ")
        self.star1_xy = wx.StaticText(self, label="(x.000,y.000)")
        self.star2_xy = wx.StaticText(self, label="(x.000,y.000)")
        self.guide = wx.ToggleButton(self, 1, size=(100,-1), label="Start Guiding")
        self.log_onoff = wx.CheckBox(self, -1, 'Guiding Log On', (10,10))
        self.guide_state = self.guide.GetValue()
        self.cadence_text = wx.StaticText(self, label="Cadence (s): ")
        self.cadence = wx.TextCtrl(self, -1, '10.0', size=(50,-1), style=wx.TE_NO_VSCROLL)

        self._DoLayout()

        self.guide.Bind(wx.EVT_TOGGLEBUTTON, self.OnGuide)

    def _DoLayout(self):
        sz = wx.GridBagSizer(vgap=3, hgap=3)

        sz.Add(self.star1, pos=(0,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.star2, pos=(1,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.star1_xy, pos=(0,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.star2_xy, pos=(1,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.guide, pos=(2,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.log_onoff, pos=(3,0), span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.cadence_text, pos=(4,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.cadence, pos=(4,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)

        self.SetSizerAndFit(sz)

    def OnGuide(self, event):
        if self.guide.GetValue():
            self.guide.SetLabel("Stop Guiding")
            self.guide.SetForegroundColour((34,139,34))
        else:
            self.guide.SetLabel("StartGuiding")
            self.guide.SetForegroundColour((0,0,0))

