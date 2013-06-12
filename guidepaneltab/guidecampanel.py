import wx

class GuideCamPanel(wx.Panel):    
    def __init__(self, parent):
        super(GuideCamPanel, self).__init__(parent)

        self.exp_text = wx.StaticText(self, -1, label="Exposure (s):")
        self.exposure = wx.TextCtrl(self, -1, '', size=(50,-1), style=wx.TE_NO_VSCROLL)
        self.exposure.SetValue('0.25')
        self.take = wx.Button(self, size=(100, -1), label="Take Image")
        self.bin_text = wx.StaticText(self, -1, label="Bin (NxN): ")
        self.bin = wx.SpinCtrl(self, id=-1, value='', min=1, max=4, initial=1, size=(40, -1))
               
        self.series = wx.SpinCtrl(self, id=-1, value='', min=1, max=1000, initial=3, size=(50, -1))
        self.series_text = wx.StaticText(self, -1, label="Series: ")
        self.scadence_text = wx.StaticText(self, -1, label="Cadence (s):")
        self.scadence = wx.TextCtrl(self, -1, '', size=(50,-1), style=wx.TE_NO_VSCROLL)
        self.scadence.SetValue('2.0')
        self.take_series = wx.ToggleButton(self, 2, size=(100, -1), label="Take Series")
        self.sname = wx.TextCtrl(self, -1, 'img', size=(130,-1), style=wx.TE_NO_VSCROLL)
        self.sname_text = wx.StaticText(self, -1, label="Series Name: ")
        self.autosave_on_text = wx.StaticText(self, label="Autosave: ")
        self.autosave_cb = wx.CheckBox(self, -1, " " , (10,10))
        self.autosave_cb.SetValue(False)
        
        self.rb_light = wx.RadioButton(self, -1, 'Light', (10, 10), style=wx.RB_GROUP)
        self.rb_dark = wx.RadioButton(self, -1, 'Dark', (10, 30))
        self.rb_flat = wx.RadioButton(self, -1, 'Flat', (10, 50))

        self._DoLayout()

    def _DoLayout(self):
        sz     = wx.GridBagSizer(vgap=3, hgap=3)

        sz.Add(self.exp_text, pos=(0,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.exposure, pos=(0,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.take, pos=(0,2), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.bin_text, pos=(0,3), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.bin, pos=(0,4), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        
        sz.Add(self.series_text, pos=(1,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.series, pos=(1,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.scadence_text, pos=(2,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.scadence, pos=(2,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)        
        sz.Add(self.sname_text, pos=(3,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.sname, pos=(3,1), span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.autosave_on_text, pos=(3,3), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.take_series, pos=(1,2), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.autosave_cb, pos=(3,4), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        
        sz.Add(self.rb_light, pos=(4,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        sz.Add(self.rb_dark, pos=(4,2), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        sz.Add(self.rb_flat, pos=(4,3), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizerAndFit(sz)
