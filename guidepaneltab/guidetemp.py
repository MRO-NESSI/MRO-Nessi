from time import sleep
import logging
import wx

from threadtools import run_async

class GuideTempPanel(wx.Panel):
    """Panel to control the temperature of the guide cam."""

    def __init__(self, parent):
        super(GuideTempPanel, self).__init__(parent)

        self.parent = parent
        
        self.temp_label = wx.StaticText(self, label="Current Temp: ")
        self.temp = wx.StaticText(self, label="...              ")
        self.settemp_label = wx.StaticText(self, label="Current Set Point (C): ")
        self.settemp_field = wx.TextCtrl(self, -1, '', size=(50,-1), style=wx.TE_NO_VSCROLL)
        self.settemp_field.SetValue('0')
        self.settemp_button = wx.Button(self, size=(80,-1), label="Set")

        self._DoLayout()
        self._DoBindings()
        self._temperatureMonitor()

    def _DoLayout(self):
        sz    = wx.GridBagSizer(vgap=3, hgap=3)
                        
        sz.Add(self.temp_label, 
               pos=(1,0), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.temp, 
               pos=(1,1), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        sz.Add(self.settemp_label, 
               pos=(2,0), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.settemp_field, 
               pos=(2,1), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        sz.Add(self.settemp_button, 
               pos=(2,2), span=(1,1),
               flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)

        self.SetSizerAndFit(sz)

    def _DoBindings(self):
        self.settemp_button.Bind(wx.EVT_BUTTON, self.OnSettemp)

    def OnSettemp(self, event):
        temp = self.settemp_field.GetValue()
        try: 
            temp = float(temp)
            if not -55 <= temp <= 45: raise Exception()
        except: 
            wx.CallAfter(wx.MessageBox,'FLI Camera has a temperature range of -55C to 45C.', 
                          'INVALID CAMERA TEMP!', wx.OK | wx.ICON_ERROR)
            logging.warning('Invalide FLI camera temperature!')
            return
        self.parent.cam.setTemperature(temp)
        logging.info('Guide cam set to %f.' % temp)

    @run_async
    def _temperatureMonitor(self):
        """Loop to monitor the temperature."""
        while True:
            wx.CallAfter(self.temp.SetLabel, str(self.parent.cam.getTemperature()))
            sleep(5)
