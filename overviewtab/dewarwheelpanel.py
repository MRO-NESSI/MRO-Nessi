import logging
import wx
from configobj import ConfigObj
cfg = ConfigObj('nessisettings.ini')


from actuators import newport
from threadtools import run_async

class WheelPanel(wx.Panel):
    """This panel controls the FLI filter wheel """
    def __init__(self, parent, name, controller, socket):
        super(WheelPanel, self).__init__(parent) 
        
        self.parent = parent
        
        # Attributes        
        self.name = cfg[name]['name']
        self.controller = controller
        self.socket = socket
        self.choices = []
        self.slots = {}
        self.position = 10
        try:
            for i in range(int(cfg[name]['slots'])):
                self.choices.append(cfg[name]['pos'+str(i)])
                self.slots[cfg[name]['pos'+str(i)]]=str(i)
        except:
            raise
#        newport.NewportInitialize(self.controller, self.name, self.socket, 0)
#        newport.NewportWheelThread(self.controller, self.name, self.socket, self.position, 0, True)
        
        self.curr_wheel_text = wx.StaticText(self, label="Current "+cfg[name]['type']+":")
        self.curr_wheel = wx.StaticText(self, label="Checking...")
        self.select_button = wx.Button(self, 1, label="Select")
        self.wheel_choice = wx.ComboBox(self, -1, size=(100,-1), choices=self.choices, style=wx.CB_READONLY)
        self.home_button = wx.Button(self, 2, label='Home')

        # Layout
        self.__DoLayout()
        
        # Event Handlers
        self.select_button.Bind(wx.EVT_BUTTON, self.move_wheel, id=1)
        self.home_button.Bind(wx.EVT_BUTTON, self.home_wheel, id=2)
        
        ## Layout for this panel:
        ##
        ##    0                      1
        ##   +-------------------+---------------------+
        ## 0 |  curr_filter_text |   curr_filter       |
        ##   +-------------------+---------------------+
        ## 1 |   select_button   |    filter_choice    |
        ##   +-------------------+---------------------+
    def __DoLayout(self):
        sbox = wx.StaticBox(self, label=self.name)
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.curr_wheel_text,  pos=(0,0), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.curr_wheel,  pos=(0,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.wheel_choice, pos=(1,0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.select_button, pos=(1,1), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.home_button, pos=(1,2), flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
    
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(200, -1))
        boxSizer.Add(sizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizerAndFit(boxSizer)

    @run_async    
    def move_wheel(self, event):
        try:
            logging.info('%s wheel moving to %s...' % (self.name, self.wheel_choice.GetSelection()))
            selected = self.wheel_choice.GetSelection()
            self.curr_wheel.SetLabel(self.choices[selected])
#           self.position =  newport.NewportWheelThread(self.controller, self.name, self.socket, self.position, self.slots[self.wheel_choice.GetValue()], True)
        except ValueError:
            pass

    @run_async
    def home_wheel(self, event):
#        self.position = newport.NewportWheelThread(self.controller, self.name, self.socket, self.position, 0, True)
        pass
        
