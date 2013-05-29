import wx

from sensors.lake import LakeshoreController

class TemperaturePanel(wx.Panel):
    
    def __init__(self, parent):
        super(TemperaturePanel, self).__init__(parent)

        self.parent = parent        

        sbox = wx.StaticBox(self, -1, 'Temperature')
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridSizer(4,2,4,4)
        self.temp_a_label = wx.StaticText(self,
                                          label = LakeshoreController.temp_probes['a']+': ')
        self.temp_b_label = wx.StaticText(self,
                                          label = LakeshoreController.temp_probes['b']+': ')
        self.temp_c_label = wx.StaticText(self,
                                          label = LakeshoreController.temp_probes['c']+': ')
        self.temp_d_label = wx.StaticText(self,
                                          label = LakeshoreController.temp_probes['d']+': ')
        
        self.temp_a = wx.StaticText(self, label = '0 K')
        self.temp_b = wx.StaticText(self, label = '0 K')
        self.temp_c = wx.StaticText(self, label = '0 K')
        self.temp_d = wx.StaticText(self, label = '0 K')

        self.temp_a_label.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.temp_b_label.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.temp_c_label.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.temp_d_label.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.temp_a.SetFont(wx.Font(13, wx.MODERN, wx.NORMAL, wx.BOLD))
        self.temp_b.SetFont(wx.Font(13, wx.MODERN, wx.NORMAL, wx.BOLD))
        self.temp_c.SetFont(wx.Font(13, wx.MODERN, wx.NORMAL, wx.BOLD))
        self.temp_d.SetFont(wx.Font(13, wx.MODERN, wx.NORMAL, wx.BOLD))

        sizer.AddMany([self.temp_a_label,
                            self.temp_a,
                            self.temp_b_label,
                            self.temp_b,
                            self.temp_c_label,
                            self.temp_c,
                            self.temp_d_label,
                            self.temp_d,])

        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
