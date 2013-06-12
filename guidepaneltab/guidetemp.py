import wx

class GuideTempPanel(wx.Panel):
    def __init__(self, parent):
        super(GuideTempPanel, self).__init__(parent)

        self.curr_temp_text = wx.StaticText(self, label="Current Temp: ")
        self.curr_temp = wx.StaticText(self, label="...              ")
        self.curr_setpoint_text = wx.StaticText(self, label="Current Set Point (C): ")
        self.curr_setpoint = wx.TextCtrl(self, -1, '', size=(50,-1), style=wx.TE_NO_VSCROLL)
        self.curr_setpoint.SetValue('0')
        self.curr_setpoint_button = wx.Button(self, size=(80,-1), label="Set")

        self._DoLayout()

    def _DoLayout(self):
        sz    = wx.GridBagSizer(vgap=3, hgap=3)
                        
        sz.Add(self.curr_temp_text, pos=(1,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.curr_temp, pos=(1,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        sz.Add(self.curr_setpoint_text, pos=(2,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.curr_setpoint, pos=(2,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        sz.Add(self.curr_setpoint_button, pos=(2,2), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)

        self.SetSizerAndFit(sz)
