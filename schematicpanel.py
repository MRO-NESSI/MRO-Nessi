class SchematicPanel(wx.Panel):
    """This panel shows the NESSI instrument diagram."""
    def __init__(self, parent, *args, **kwargs):
        super(SchematicPanel, self).__init__(parent)
        
        self.parent = parent
        # Attributes
        self.schematic = wx.StaticBitmap(self)
        self.schematic.SetFocus()
        self.schematic.SetBitmap(wx.Bitmap('media/nessi_fullimage.png'))
        
        # Layout
        self.__DoLayout()
        
        # Event handlers
        
    def __DoLayout(self):
        ## Layout for this panel:
        ##    0               
        ##   +---------------+
        ## 0 |     Logo      |
        ##   +---------------+
        sbox = wx.StaticBox(self, label="")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.schematic, pos=(0,0), flag=wx.ALIGN_CENTER)
        
        # Add the grid bag to the static box and make everything fit
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
