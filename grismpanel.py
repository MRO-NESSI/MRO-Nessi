import wx

class GrismPanel(wx.Panel):
    """This panel controls the Grism wheel"""
    def __init__(self, parent, *args, **kwargs):
        super(GrismPanel, self).__init__(parent) 
        
        self.parent = parent

        # Attributes        
        self.grism = ['j', 'h', 'k', 'Open']
    
        self.curr_grism_text = wx.StaticText(self, label="Current Grism:")
        self.curr_grism = wx.StaticText(self, label="Checking...")
        self.select_button = wx.Button(self, label="Select")
        self.grism_choice = wx.ComboBox(self, -1, size=(100,-1), choices=self.grism, style=wx.CB_READONLY)
    
        # Layout
        self.__DoLayout()
        # Event handlers
        self.Bind(wx.EVT_COMBOBOX, self.on_select, self.grism_choice)
        self.Bind(wx.EVT_BUTTON, self.move_grism, self.select_button)
        
    def __DoLayout(self):
        ## Layout for this panel:
        ##
        ##    0                      1
        ##   +--------------------+---------------------+
        ## 0 |  curr_filter_text  |   curr_filter       |
        ##   +-------------------+----------------------+
        ## 1 |   select_button   |    filter_choice     |
        ##   +-------------------+----------------------+
        
        sbox = wx.StaticBox(self, label="Grism")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.curr_grism_text,  pos=(0,0), flag=wx.ALIGN_LEFT)
        sizer.Add(self.curr_grism,  pos=(0,1), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.grism_choice, pos=(1,0), flag=wx.ALIGN_CENTER)
        sizer.Add(self.select_button, pos=(1,1), flag=wx.ALIGN_CENTER)
    
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(200, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
        
    def on_select(self, event):
        try:
            selected = event.GetSelection()
            pub.sendMessage("LOG EVENT", "Chosen Grism is..." + str(self.grism[selected]))
            return selected
        except ValueError:
            pass

    def move_grism(self, event):
        try:
            pub.sendMessage("LOG EVENT", "Moving to Grism...")
            selected = self.grism_choice.GetSelection()
            self.curr_grism.SetLabel(self.grism[selected])
        except ValueError:
            pass        

