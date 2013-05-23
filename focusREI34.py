import wx

class FocusREI34(wx.Panel):
    """This panel controls the position of REI1-2 """
    def __init__(self, parent, *args, **kwargs):
        super(FocusREI34, self).__init__(parent) 
        
        self.parent = parent

        # Attributes    
        self.curr_pos_label = wx.StaticText(self, label="Position " + u'\u03bc' + "m:")
        self.curr_pos = wx.StaticText(self, label="...")
        
        self.goto_button = wx.Button(self, label="Set", size=(50,-1))
        self.goto_value = wx.TextCtrl(self, -1, '', size=(50,-1), style=wx.TE_NO_VSCROLL)
        
        self.up_button = wx.Button(self, label=u'\u21e7' + " Up", size=(60,-1), style=wx.BU_LEFT)
        self.step_size = wx.SpinCtrl(self, -1, '', (-1, -1),  (50, -1))
        self.step_size.SetRange(1, 1000)
        self.step_size.SetValue(0)
        self.down_button = wx.Button(self, label= u'\u21e9' + "Down ", size=(60,-1), style=wx.BU_LEFT)
        
        # Layout
        self.__DoLayout()
        
        # Event Handlers
        
        ## Layout for this panel:
        ##
        ##    0                      1
        ##   +-------------------+---------------------+
        ## 0 |  curr_pos_label   |   curr_pos          |
        ##   +-------------------+---------------------+
        ## 1 |     in_button     |      out_button     |
        ##   +-------------------+---------------------+
    def __DoLayout(self):
        sbox = wx.StaticBox(self, label="Focus REI-3-4")
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.curr_pos_label,  pos=(0,0), span=(1,2), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.curr_pos,  pos=(0,2), span=(1,2), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
        
        sizer.Add(self.goto_button, pos=(1,3), span=(1,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.goto_value, pos=(2,3), span=(1,1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
    
        sizer.Add(self.up_button, pos=(1,0), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.step_size, pos=(1,2), span=(1,1), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.down_button, pos=(2,0), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(150, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)        
        
        
