import wx

class MaskPanel(wx.Panel):
    """This panel controls the mask wheel."""
    def __init__(self, parent, *args, **kwargs):
        super(MaskPanel, self).__init__(parent) 
        
        self.parent = parent

        # Attributes        
        self.masks = ['Field 1', 'Field 2', 'Field 3', 'Field 4', 'Open', 'Dark']#settings.mask 
        
        self.curr_mask_text = wx.StaticText(self, label="Current Mask:")
        self.curr_mask = wx.StaticText(self, label="Checking...")
        self.select_button = wx.Button(self, label="Select")
        self.mask_choice = wx.ComboBox(self, -1, size=(100,-1), choices=self.masks, style=wx.CB_READONLY)
        
        # Layout
        self.__DoLayout()
        
        # Event handlers
        self.Bind(wx.EVT_COMBOBOX, self.on_select, self.mask_choice)
        self.Bind(wx.EVT_BUTTON, self.move_mask, self.select_button)
        
    def __DoLayout(self):
        ## Layout for this panel:
        ##
        ##    0                      1
        ##   +--------------------+---------------------+
        ## 0 |  curr_mask_text   |   curr_mask          |
        ##   +-------------------+----------------------+
        ## 1 |   select_button   |    mask_choice       |
        ##   +-------------------+----------------------+
        
        sbox = wx.StaticBox(self, label="Mask Wheel")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        # Add controls to gridbag
        sizer.Add(self.curr_mask_text,  pos=(0,0), flag=wx.ALIGN_LEFT)
        sizer.Add(self.curr_mask,  pos=(0,1), flag=wx.ALIGN_RIGHT)
        sizer.Add(self.mask_choice, pos=(1,0), flag=wx.ALIGN_CENTER)
        sizer.Add(self.select_button, pos=(1,1), flag=wx.ALIGN_CENTER)
    
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(200, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)
       
    def on_select(self, event):
        try:
            selected = event.GetSelection()
            pub.sendMessage("LOG EVENT", "Chosen mask is..." + self.masks[selected])
            return selected
        except ValueError:
            pass

    def move_mask(self, event):
        try:
            pub.sendMessage("LOG EVENT", "Moving to mask...")
            selected = self.mask_choice.GetSelection()
            print selected
            maskchoice = 'setINDI "FLI Wheel.FILTER_SLOT.FILTER_SLOT_VALUE=5"'
            print maskchoice
            #mask = subprocess.Popen(maskchoice, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #stdout_text, stderr_text = mask.communicate()
            #print stdout_text, stderr_text
            self.curr_mask.SetLabel(self.masks[selected])
        except ValueError:
            pass

        
