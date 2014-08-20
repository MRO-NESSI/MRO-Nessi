"""
.. module:: guidecampanel.py
   :platform: Unix
   :synopsis: A panel to deal with guidecam interface.
   
.. moduleauthor:: Tyler Cecil <tcecil@mro.nmt.edu>

"""

import logging

from time import sleep
from threading import Event
import wx

from threadtools import run_async, callafter

import datetime

AUTOSAVE_FNAME = 'autosave/GuideCam_%m-%d-%Y_%H:%M:%S:%f.fits'

class GuideCamPanel(wx.Panel):    
    def __init__(self, parent):
        super(GuideCamPanel, self).__init__(parent)

        self.parent = parent

        #Exposure Time
        ################################################################
        self.exp_text = wx.StaticText(self, -1, label="Exposure (s):")
        self.exposure = wx.TextCtrl(self, -1, '', size=(50,-1), 
                                    style=wx.TE_NO_VSCROLL)
        self.exposure.SetValue('0.25')

        #Take Image Button
        ################################################################
        self.take = wx.Button(self, size=(100, -1), 
                              label="Take Image")

        #Binning
        ################################################################
        self.bin_text = wx.StaticText(self, -1, label="Bin (NxN): ")
        self.bin      = wx.SpinCtrl(self, id=-1, value='', 
                                    min=1, max=4, initial=1, 
                                    size=(40, -1))
        
        #Series Controll Settings
        ################################################################
        self.series        = wx.SpinCtrl(self, id=-1, value='', min=1, 
                                        max=1000, initial=3, 
                                        size=(50, -1))
        self.series_text   = wx.StaticText(self, -1, label="Series: ")
        self.scadence_text = wx.StaticText(self, -1, label="Cadence (s):")
        self.scadence      = wx.TextCtrl(self, -1, '', size=(50,-1), 
                                         style=wx.TE_NO_VSCROLL)
        self.scadence.SetValue('2.0')

        self.sname            = wx.TextCtrl(self, -1, 'img', size=(130,-1), 
                                            style=wx.TE_NO_VSCROLL)
        self.sname_text       = wx.StaticText(self, -1, 
                                              label="Series Name: ")
        self.autosave_on_text = wx.StaticText(self, label="Autosave: ")
        self.autosave_cb      = wx.CheckBox(self, -1, " " , (10,10))
        self.autosave_cb.SetValue(False)


        #Take Series Button
        ################################################################
        self.take_series = wx.ToggleButton(self, 2, size=(100, -1), 
                                           label="Take Series")


        #Lighting Radio Buttons
        ################################################################
        self.rb_light = wx.RadioButton(self, -1, 'Light', (10, 10), 
                                       style=wx.RB_GROUP)
        self.rb_dark  = wx.RadioButton(self, -1, 'Dark', (10, 30))
        self.rb_flat  = wx.RadioButton(self, -1, 'Flat', (10, 50))

        self._DoLayout()
        self._DoBindings()

    def _DoLayout(self):
        sz     = wx.GridBagSizer(vgap=3, hgap=3)

        sz.Add(self.exp_text, pos=(0,0), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.exposure, pos=(0,1), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.take, pos=(0,2), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.bin_text, pos=(0,3), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.bin, pos=(0,4), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.series_text, pos=(1,0), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.series, pos=(1,1), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.scadence_text, pos=(2,0), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.scadence, pos=(2,1), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL)        
        sz.Add(self.sname_text, pos=(3,0), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.sname, pos=(3,1), span=(1,2), 
               flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.autosave_on_text, pos=(3,3), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        sz.Add(self.take_series, pos=(1,2), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL)
        sz.Add(self.autosave_cb, pos=(3,4), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)

        sz.Add(self.rb_light, pos=(4,1), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        sz.Add(self.rb_dark, pos=(4,2), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        sz.Add(self.rb_flat, pos=(4,3), span=(1,1), 
               flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizerAndFit(sz)

    def _DoBindings(self):
        self.take.Bind(wx.EVT_BUTTON, self.OnExpose)
        self.take_series.Bind(wx.EVT_TOGGLEBUTTON, self.OnExposeSeries)
        self.bin.Bind(wx.EVT_SPINCTRL, self.OnBin)

    def OnExpose(self, event):
        try:
            self.setExposure()
        except:
            return
        self.takePicture()

    @callafter
    def takePicture(self):
        #Take Image
        i = self.parent.cam.takePictureFITS()
        self.parent.DisplayImage(i)
        self.parent.d.set('zoom to fit')

        if self.autosave_cb.GetValue():
            fname = datetime.datetime.now().strftime(AUTOSAVE_FNAME)
            try:
                with open(fname, 'wb') as image:
                    i.writeto(image)
                    image.close()
                    print('Image autosaved to ' + fname)
            except IOError as e:
                wx.MessageBox('Warning, image could not be autosaved!',
                              'FILE IO ERROR!', wx.OK | wx.ICON_ERROR)

    @callafter
    def OnExposeSeries(self, event):
        if self.take_series.GetValue():
            count   = self.series.GetValue()
            cadence = self.scadence.GetValue()
            try:
                cadence = float(cadence)
            except:
                wx.CallAfter(wx.MessageBox,'Please select cadence time in seconds!',
                             'INVALID EXPOSURE TIME!', wx.OK | wx.ICON_ERROR)
                self.endSeries()
                return

            self.take.Enable(False)
            self.take_series.SetLabel('Cancel Series')
            self.take_series.SetForegroundColour((34,139,34))
            self._series_stop = Event()
            self.Series(count, cadence)
        else:
            self._series_stop.set()

            
    def OnBin(self, event):
        h = self.bin.GetValue()
        self.parent.cam.setBinning(h,h)


    def setExposure(self):
        #Set the exposure time
        try:
            self.parent.cam.setExposure(int(1000*float(self.exposure.GetValue())))
        except:
            wx.CallAfter(wx.MessageBox,'Please select exposure time in secconds!', 
                          'INVALID EXPOSURE TIME!', wx.OK | wx.ICON_ERROR)
            raise

    
    @run_async(daemon=True)
    def Series(self, count, cadence):
        try:
            self.setExposure()
        except:
            self.endSeries()
            return

        for i in range(0, count):
            if self._series_stop.isSet():
                break
            self.takePicture()
            logging.debug("Guide cam series: %i of %i" % (i, count))
            sleep(cadence)
        self.endSeries()
        

    @callafter
    def endSeries(self):
        self.take_series.SetLabel("Take Series")
        self.take_series.SetForegroundColour((0,0,0))
        self.take.Enable(True)
        self.take_series.SetValue(False)
