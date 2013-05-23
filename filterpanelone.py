import wx

class FilterPanelOne(wx.Panel):
    """This panel controls the FLI filter wheel """
    def __init__(self, parent, *args, **kwargs):
        super(FilterPanelOne, self).__init__(parent) 
        
        self.parent = parent

        # Attributes
        self.filters = ['J', 'H', 'K', 'Open']
    
        self.curr_filter_text = wx.StaticText(self, label="Current Filter:")
        self.curr_filter = wx.StaticText(self, label="Checking...")
        self.select_button = wx.Button(self, label="Select")
        self.filter_choice = wx.ComboBox(self, -1, size=(100,-1), choices=self.filters, style=wx.CB_READONLY)
        
        # Layout
        self.__DoLayout()
        
        # Event Handlers
        self.filter_choice.Bind(wx.EVT_COMBOBOX, self.on_select)
        self.select_button.Bind(wx.EVT_BUTTON, self.move_filter)
        
        ## Layout for this panel:
        ##
        ##    0                      1
        ##   +-------------------+---------------------+
        ## 0 |  curr_filter_text |   curr_filter       |
        ##   +-------------------+---------------------+
        ## 1 |   select_button   |    filter_choice    |
        ##   +-------------------+---------------------+
    def __DoLayout(self):
        sbox = wx.StaticBox(self, label="Filter Wheel One")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.curr_filter_text,  pos=(0,0), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.curr_filter,  pos=(0,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.filter_choice, pos=(1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.select_button, pos=(1,1), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
    
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(200, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        
    def on_select(self, event):
        try:
            selected = event.GetSelection()
            status_update = "Chosen filter is..." + str(self.filters[selected])
            pub.sendMessage("LOG EVENT", status_update)
            return selected
        except ValueError:
            pass

    def move_filter(self, event):
        try:
            pub.sendMessage("LOG EVENT", "Moving to filter...")
            selected = self.filter_choice.GetSelection()
            self.curr_filter.SetLabel(self.filters[selected])
        except ValueError:
            pass
        
