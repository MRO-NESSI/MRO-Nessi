import logging
from time import sleep
from threading import Event
import re

import wx

from threadtools import run_async
from instrument.instrument import InstrumentError

class GuidingPanel(wx.Panel):
    """Sub-pannel for guidecam GUIDING. Controls either
    single or double star tracking"""

    def __init__(self, parent):
        super(GuidingPanel, self).__init__(parent)

        #Attributes
        ################################################################
        self.parent = parent

        #Star Labels
        ################################################################
        self.star1    = wx.StaticText(self, label="Star 1: ")
        self.star2    = wx.StaticText(self, label="Star 2: ")
        self.star1_xy = wx.StaticText(self, label="(x.000,y.000)")
        self.star2_xy = wx.StaticText(self, label="(x.000,y.000)")

        #Start Guiding Button
        ################################################################
        self.guide = wx.ToggleButton(self, 1, size=(100,-1), label="Start Guiding")

        #Logging Option Button
        ################################################################
        self.log_onoff = wx.CheckBox(self, -1, 'Guiding Log On', (10,10))

        #Cadence
        ################################################################
        self.cadence_text = wx.StaticText(self, label="Cadence (s): ")
        self.cadence      = wx.TextCtrl(self, -1, '10.0', size=(50,-1), 
                                        style=wx.TE_NO_VSCROLL)

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
            self.StartGuide()
        else:
            self.StopGuide()

    def StartGuide(self):
        self.parent.guideCamPanel.Enable(False)
        self.guide.SetLabel("Stop Guiding")
        self.guide.SetForegroundColour((34,139,34))
        self._guide_stop = Event()
        self.guide_routine()

    def StopGuide(self):
        self.guide.SetLabel("StartGuiding")
        self.guide.SetForegroundColour((0,0,0))
        self._guide_stop.set()
        self.guide.SetValue(False)
        self.parent.guideCamPanel.Enable(True)


    def getInitialXY(self):
        #Get Ds9 object
        d             = self.parent.d
        region_string = d.get('regions')
        
        #Use a regular expression to find region coords
        results = re.findall(
            r'point\(([0-9]*\.[0-9]*)\,([0-9]*\.[0-9]*)\)', 
            region_string)
        
        if len(results) is 1:
            return (float(results[0][0]), float(results[0][1]))
        return None

    @run_async(daemon=True)
    def guide_routine(self):
        logging.info('getting initialxy...')
        initialxy   = self.getInitialXY()
        logging.info('done getting intialxy!')
        t0_centroid = None
        tn_centroid = None
        fits_file   = None

        if not initialxy:
            wx.CallAfter(
                wx.MessageBox,'Please select a point in ds9!', 
                'NO INITIAL XY!', wx.OK | wx.ICON_ERROR)
            self.StopGuide()
            return

        
        cadence     = self.cadence.GetValue()
        try:
            cadence = float(cadence)
        except:
            wx.CallAfter(
                wx.MessageBox,'Please select cadence time in secconds!', 
                'INVALID EXPOSURE TIME!', wx.OK | wx.ICON_ERROR)
            self.StopGuide()
            return

        logging.info("Begging Guiding...")

        try:
            fits_file = self.parent.instrument.guide_cam.takePictureFITS()
            t0_centroid = tn_centroid = self.parent.instrument.get_centroid(
                fits_file , initialxy)
        except InstrumentError:
            logging.error("Could not get guiding centroid!")
            self.StopGuide()
            return

        logging.info("t0_centroid aquired...")
        
        while not self._guide_stop.isSet():
            fits_file = self.parent.instrument.guide_cam.takePictureFITS()

            try:
                tn_centroid = self.parent.instrument.get_centroid(
                    fits_file, tn_centroid.xyCtr)
            except InstrumentError:
                logging.error("Could not get guiding centroid!")
                self.StopGuide()
                return

            logging.info("tn_centroid aquired...")

            new_sky = self.parent.instrument.calc_xy_shift(t0_centroid, 
                                                    tn_centroid,
                                                    fits_file[0].header)
            logging.info("Moving telescope to new sky vector: [%f, %f]" 
                         % (new_sky[0][0] / 15.0, new_sky[0][1]))
            
            # convert RA in decimal degrees back to RA in decimal hours
            #self.telescope.ra  = new_sky[0][0] / 15.0
            #self.telesceop.dec = new_sky[0][1]
            
            logging.info("Sleeping for %f" % cadence)
            sleep(cadence)
