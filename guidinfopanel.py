class GuideInfoPanel(wx.Panel):
    """This panel shows information on the guide camera system."""
    def __init__(self, parent, *args, **kwargs):
        super(GuideInfoPanel, self).__init__(parent)

        self.parent = parent
        
        # Attributes 
        self.curr_centroids_text = wx.StaticText(self, label="Current Centroids: ")
        self.curr_centroids = wx.StaticText(self, label="s1 = (0,0)  s2 = (0,0)")
        
        self.plotCanvas = GuidePlotPanel(self)
        self.reset = wx.Button(self, size=(50,-1), label="Reset Plot")
        #self.guide_hist = wx.StaticBitmap(self)
        #self.guide_hist.SetFocus()
        #self.guide_hist.SetBitmap(wx.Bitmap('guide_err.png'))
        # Layout
        self.__DoLayout()
        
        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.ResetPlot, self.reset)

    def __DoLayout(self):
        ## Layout for this panel:
        ##
        ##    0               1
        ##   +---------------+---------------+
        ## 0 | curr_ra_text  | self.curr_ra  |
        ##   +---------------+---------------+
        ## 1 | curr_dec_text | self.new_dec  |
        ##   +---------------+---------------+
        ##
        sbox = wx.StaticBox(self, label="Guide Status")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)
        
        # Add controls to gridbag
        sizer.Add(self.curr_centroids_text, pos=(0,0), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.curr_centroids, pos=(0,1), span=(1,1), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.plotCanvas, pos=(2,0), span=(10,4), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND)
        sizer.Add(self.reset, pos=(1,0), span=(1,1), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND)
        
        #sizer.Add(self.guide_hist, pos=(3,0), span=(1,2), flag=wx.ALIGN_CENTER_HORIZONTAL)
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(300, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        
        #subscribe to xy updates
        pub.subscribe(self.UpdatePanel, "xyupdate")


    def ResetPlot(self, event):
        self.plotCanvas.data_clear()
    
    def UpdatePanel(self, s1centroid):
        print s1centroid.data[0], s1centroid.data[1]
        self.curr_centroids.SetLabel('s1=('+ str(round(s1centroid.data[0], 2))+','+ str(round(s1centroid.data[1],2))+'), s2=(0,0)')
                                 

