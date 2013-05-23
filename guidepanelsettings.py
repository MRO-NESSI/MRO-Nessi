import ds9
import threading
import threadtools
import time
import usb.core
import wx

DEBUG = False

class GuidePanelSettings(wx.Panel):
    """This panel controls the guide camera settings"""
    def __init__(self, parent, *args, **kwargs):
        super(GuidePanelSettings, self).__init__(parent)
 
        self.parent = parent
        #Is the camera connected and ready to go
        self.c_power = False
        #is the guiding log turned on
        self.guide_log_status = False
        #current status of the camera
        self.status = None
        #current status of guiding
        self.guidestatus = threading.Event()
        #current status of image sequence
        self.seriesstatus = threading.Event()
        #True if waiting for camera to show up on USB bus
        self.looking = True
        #camera instance
        self.cam0 = None
                
        #guide
        self.star1 = wx.StaticText(self, label="Star 1: ")
        self.star2 = wx.StaticText(self, label="Star 2: ")
        self.star1_xy = wx.StaticText(self, label="(x.000,y.000)")
        self.star2_xy = wx.StaticText(self, label="(x.000,y.000)")
        self.guide = wx.ToggleButton(self, 1, size=(100,-1), label="Guiding Off")
        self.log_onoff = wx.CheckBox(self, -1, 'Guiding Log On', (10,10))
        self.guide_state = self.guide.GetValue()
        self.cadence_text = wx.StaticText(self, label="Cadence (s): ")
        self.cadence = wx.TextCtrl(self, -1, '10.0', size=(50,-1), style=wx.TE_NO_VSCROLL)
                
        #stat
        self.curr_temp_text = wx.StaticText(self, label="Current Temp: ")
        self.curr_temp = wx.StaticText(self, label="...              ")
        self.curr_setpoint_text = wx.StaticText(self, label="Current Set Point (C): ")
        self.curr_setpoint = wx.TextCtrl(self, -1, '', size=(50,-1), style=wx.TE_NO_VSCROLL)
        self.curr_setpoint.SetValue('0')
        self.curr_setpoint_button = wx.Button(self, size=(80,-1), label="Set")
        
        #exp
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
        
        # Layout
        self.__DoLayout()
        
        # Event Handlers
        
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnGuide, id=1)
        self.Bind(wx.EVT_BUTTON, self.Expose, self.take)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.ExposeSeries, id=2)
        self.Bind(wx.EVT_BUTTON, self.SetPoint, self.curr_setpoint_button)
        
        self.Bind(wx.EVT_CHECKBOX, self.GuideLog, self.log_onoff)
        
        self.Bind(wx.EVT_SPINCTRL, self.Bin, self.bin)

        # Start up image display
        self.d = ds9.ds9()
        self.d.set("width 538")
        self.d.set("height 528")
        # Look for camera and initialize it
        self.__OnPower()
        
    def __OnPower(self):
        startlook = time.time()
        while self.looking:
            dev = usb.core.find(idVendor=0x0f18, idProduct=0x000a)
            if DEBUG: print dev
            
            if dev is None:
                time.sleep(0.5)
                if DEBUG: print time.time()
                if time.time()-startlook > 5:
                    self.looking = False
                    break
            if dev != None:
                self.looking = False
                self.c_power = True
                cams = FLI.camera.USBCamera.find_devices()
                self.cam0 = cams[0]
                self.cam0.set_bit_depth("16bit")
                temp = self.cam0.get_temperature()
                self.curr_temp.SetLabel(str(temp) + u'\N{DEGREE SIGN}' + 'C  ')
                
    def OffPower(self):
        self.c_power = False
        self.looking = True
        self.curr_temp.SetLabel('...')
        self.c.shutdown()
        self.c = None
        
    def __DoLayout(self):
        # make sizers
        guide_sz   = wx.GridBagSizer(vgap=3, hgap=3)
        stat_sz    = wx.GridBagSizer(vgap=3, hgap=3)
        exp_sz     = wx.GridBagSizer(vgap=3, hgap=3)
                        
        # add attributes to sizers
        exp_sz.Add(self.exp_text, pos=(0,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        exp_sz.Add(self.exposure, pos=(0,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        exp_sz.Add(self.take, pos=(0,2), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        exp_sz.Add(self.bin_text, pos=(0,3), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        exp_sz.Add(self.bin, pos=(0,4), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        
        exp_sz.Add(self.series_text, pos=(1,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        exp_sz.Add(self.series, pos=(1,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        exp_sz.Add(self.scadence_text, pos=(2,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        exp_sz.Add(self.scadence, pos=(2,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)        
        exp_sz.Add(self.sname_text, pos=(3,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        exp_sz.Add(self.sname, pos=(3,1), span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        exp_sz.Add(self.autosave_on_text, pos=(3,3), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        exp_sz.Add(self.take_series, pos=(1,2), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        exp_sz.Add(self.autosave_cb, pos=(3,4), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        
        exp_sz.Add(self.rb_light, pos=(4,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        exp_sz.Add(self.rb_dark, pos=(4,2), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        exp_sz.Add(self.rb_flat, pos=(4,3), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
                      
        guide_sz.Add(self.star1, pos=(0,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        guide_sz.Add(self.star2, pos=(1,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        guide_sz.Add(self.star1_xy, pos=(0,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        guide_sz.Add(self.star2_xy, pos=(1,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        guide_sz.Add(self.guide, pos=(2,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        guide_sz.Add(self.log_onoff, pos=(3,0), span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL)
        guide_sz.Add(self.cadence_text, pos=(4,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
        guide_sz.Add(self.cadence, pos=(4,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                
        stat_sz.Add(self.curr_temp_text, pos=(1,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        stat_sz.Add(self.curr_temp, pos=(1,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        stat_sz.Add(self.curr_setpoint_text, pos=(2,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
        stat_sz.Add(self.curr_setpoint, pos=(2,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
        stat_sz.Add(self.curr_setpoint_button, pos=(2,2), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
                        
        # Set up master StaticBox
        sbox = wx.StaticBox(self, label="Guide Camera")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=5, hgap=5)      
        
        # add sizers to master sizer
        sizer.Add(exp_sz,       pos=(0,0), span=(1,3))
        sizer.Add(wx.StaticLine(self),   pos=(1,0), span=(1,3), flag=wx.EXPAND|wx.BOTTOM)
        sizer.Add(stat_sz,      pos=(2,0), span=(1,1))
        sizer.Add(wx.StaticLine(self, -1, style=wx.LI_VERTICAL),   pos=(2,1), span=(1,1), flag=wx.EXPAND)
        sizer.Add(guide_sz,     pos=(2,2), span=(1,1), flag=wx.EXPAND)
        
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        
        # Set up a timer to update camera info
        TIMER_ID = 130 # Random number; it doesn't matter
        self.timer = wx.Timer(self, TIMER_ID)
        self.timer.Start(10000) # poll every 20 seconds
        wx.EVT_TIMER(self, TIMER_ID, self.on_timer)

    def on_timer(self, event):
        try:
            if not self.c_power:
                pass
            else:
                #get current temp
                temp = self.cam0.get_temperature()
                self.curr_temp.SetLabel(str(temp) + u'\N{DEGREE SIGN}' + 'C  ')
                            
        except ValueError:
            pass
        
    @threadtools.callafter
    def DisplayImage(self, event, image):
        image[:] = np.fliplr(image)[:]
        self.d.set_np2arr(image)
        self.d.set("zoom to fit")
        
    def updateKeywords(self):
        """Update the keywords for the FITS file header"""
        global keywords
#        #TelescopePanel.scope_update(self.parent.TelescopePanel)
        if self.rb_light.GetValue():
            light = True
            keywords["IMGTYPE"] = "Light"
        if self.rb_dark.GetValue():
            light = False
            keywords["IMGTYPE"] = "Dark"
        if self.rb_flat.GetValue():
            light = True
            keywords["IMGTYPE"] = "Flat"
        #get name for header
        name = self.sname.GetValue()

        keywords["OBSERVER"] = str(self.parent.parent.GetPage(3).observerTxt.GetValue())
        keywords["FILENAME"] = str(self.sname.GetValue())
        keywords["RA"]       = 0
        keywords["DEC"]      = 0
        keywords["AIRMASS"]  = 0 
        keywords["TELALT"]   = 0 
        keywords["TELAZ"]    = 0
        keywords["TELFOCUS"] = 0 
        keywords["PA"]       = 0 
        keywords["JD"]       = 0 
        keywords["GDATE"]    = 0 
        keywords["WINDVEL"]  = 0 
        keywords["WINDGUST"] = 0 
        keywords["WINDDIR"]  = 0 
        keywords["REI12"]    = 0 
        keywords["REI34"]    = 0 
        keywords["MASK"]     = 0
        keywords["FILTER1"]  = 0 
        keywords["FILTER2"]  = 0
        keywords["GRISM"]    = 0
        keywords["EXP"]      = float(self.exposure.GetValue())
        keywords["CAMTEMP"]  = float(self.cam0.get_temperature())
        keywords["CRPIX1"]   = 0
        keywords["CRPIX2"]   = 0
        keywords["CDELT1"]   = float(self.parent.parent.GetPage(3).pixelscalexTxt.GetValue())
        keywords["CDELT2"]   = float(self.parent.parent.GetPage(3).pixelscaleyTxt.GetValue())
        keywords["CRVAL1"]   = 0
        keywords["CRVAL2"]   = 0
        keywords["CROTA2"]   = 0

    def updateHeader(self, fitsfile):
        """Update the header of the fits file to be saved"""
        
            
    def Expose(self, event):
        """take an exposure with current settings"""
        # Set exposure time
        self.cam0.set_exposure(int(1000*float(self.exposure.GetValue())))
        # Update header info
        self.updateKeywords()
        # take image
        self.image = self.cam0.take_photo()
        
#        self.fits = pic.UpdateFitsHeader(self.fits, keywords, name)
        #send image to the display
        self.DisplayImage(event, self.image)
        autosave = self.autosave_cb.GetValue()
        if autosave:
            # Make Fits File
            filename = keywords["FILENAME"]
            ftime = keywords["GDATE"]
            hdu = pyfits.PrimaryHDU(self.image)
            hdulist = pyfits.HDUList([hdu])
            hdulist.writeto(str(self.parent.parent.GetPage(3).savefolderTxt.GetValue())+filename+ftime+".fits")
            
            
    def ExposeSeries(self, event):
        if self.take_series.GetValue():
            pub.sendMessage("LOG EVENT", "Image Series Started...")
            scount = self.series.GetValue()
            scadence = self.scadence.GetValue()
            self.take_series.SetLabel("Cancel")
            self.take_series.SetForegroundColour((34,139,34))
            self.exp_series_thread = SeriesExpThread(self, event, scount, scadence)
            self.exp_series_thread.daemon=True
            self.seriesstatus.set()
            self.exp_series_thread.start()
        else:
            self.SeriesCancel("Series Stopped...")
#            pub.sendMessage("LOG EVENT", "Series Stopped...")
#            self.take_series.SetLabel("Take Series")
#            self.take_series.SetForegroundColour((0,0,0))
#            self.seriesstatus.clear()
#            self.exp_series_thread.join()
            
    def Bin(self, event):
        h = self.bin.GetValue()
        self.cam0.set_image_binning(h,h)
        
    def SetPoint(self, event):
        temp = int(self.curr_setpoint.GetValue())
        self.cam0.set_temperature(temp)
                
    def ChooseStar1(self, event):
        global s1
        s1 = event.GetPosition()
        #display PyGuide coordinate system
            
        self.pgcoord = pic.scale_coord_to_cam(s1, self.max_size, self.roiH.GetValue())
        self.pgcoord = pic.coord_flip(self.pgcoord,self.roiH.GetValue())
        if DEBUG: print 's1', s1, 'roiH', self.roiH.GetValue()
        self.star1_xy.SetLabel(str(self.pgcoord))
        self.DisplayImage(event, self.image)
        
    def ChooseStar2(self, event):
        global s2
        s2 = event.GetPosition()
        self.star2_xy.SetLabel(str(s2))
        self.DisplayImage(event, self.image)
    
    def OnGuide(self, event):
        try:
            if not self.c_power:
                wx.Bell()
                wx.MessageBox('The guide camera does not have power.', style=wx.OK|wx.CENTER)
                self.guide.SetValue(False)
            else:
                if self.guide.GetValue(): 
                    pub.sendMessage("LOG EVENT", "Guiding Started...")
                    self.guide.SetLabel("Guiding On")
                    self.guide.SetForegroundColour((34,139,34))
                    #get variables to pass to guide routine
                    cadence = float(self.cadence.GetValue())
                    if DEBUG: print cadence
                    self.guide_thread = GuideThread(self, self.pgcoord , cadence)
                    self.guide_thread.daemon=True
                    self.guidestatus.set()
                    self.guide_thread.start()
                else:
                    pub.sendMessage("LOG EVENT", "Guiding Stopped...")
                    self.guide.SetLabel("Guiding Off")
                    self.guide.SetForegroundColour((0,0,0))
                    self.guidestatus.clear()
                    self.guide_thread.join()
                    
        except ValueError:
            pass
    
    @threadtools.callafter
    def GuideError(self, error):
        pub.sendMessage("LOG EVENT", error)
        self.guide.SetLabel("Guiding Off")
        self.guide.SetForegroundColour((0,0,0))
        self.guide.SetValue(False)
        self.guidestatus.clear()
        self.guide_thread.join()
        wx.Bell()
        wx.MessageBox(error, style=wx.OK|wx.CENTER)

    @threadtools.callafter
    def Update(self, shift, currentxy):
        pub.sendMessage("shiftupdate", shift)
        pub.sendMessage("xyupdate", currentxy)
        
    @threadtools.callafter
    def SeriesUpdate(self, image, total):
        pub.sendMessage("change_statusbar", "Image " + str(image+1) + " of " + str(total)) 
        
    @threadtools.callafter
    def SeriesCancel(self, error):
        pub.sendMessage("LOG EVENT", error)
        pub.sendMessage("change_statusbar", error)
        self.take_series.SetLabel("Take Series")
        self.take_series.SetForegroundColour((0,0,0))
        self.take_series.SetValue(False)
        self.seriesstatus.clear()
        self.exp_series_thread.join()
        
    def GuideLog(self, event):
        if self.log_onoff.GetValue():
            self.guide_log_status = True
            pub.sendMessage("LOG EVENT", 'Guide Logging On')
        else:
            self.guide_log_status = False
            pub.sendMessage("LOG EVENT", 'Guide Logging Off')
            pass

