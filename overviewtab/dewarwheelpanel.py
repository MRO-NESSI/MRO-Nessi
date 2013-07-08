import wx

from threadtools          import run_async
from instrument.component import InstrumentError

class WheelPanel(wx.Panel):
    """This panel controls the FLI filter wheel."""

    def __init__(self, parent, name, wheel):
        """Makes a WheelPanel.
        
        Arguments:
            parent -- Parent panel
            name   -- String name of the panel. Used for title text.
            wheel  -- DewarWheel object.

        Raises:
            None
        """
        super(WheelPanel, self).__init__(parent) 
        
        self.parent = parent
        
        # Attributes
        ################################################################
        self.name    = name
        self.wheel   = wheel
        self.choices = wheel.positions
        
        #GUI Components
        ################################################################
        self.curr_wheel_text = wx.StaticText(
            self, label="Current Position:")
        self.curr_wheel      = wx.StaticText(
            self, label=self.wheel.position)
        self.select_button   = wx.Button(
            self, 1, label="Select")
        self.wheel_choice    = wx.ComboBox(
            self, -1, size=(100,-1), choices=self.choices, 
            style=wx.CB_READONLY)
        self.home_button = wx.Button(self, 2, label='Home')

        # Layout
        ################################################################
        self.__DoLayout()
        
        # Event Handlers
        ################################################################
        self.select_button.Bind(wx.EVT_BUTTON, self.OnSelect, id=1)
        self.home_button.Bind(wx.EVT_BUTTON, self.OnHome, id=2)
        

    def __DoLayout(self):
        sbox     = wx.StaticBox(self, label=self.name)
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)
        sizer    = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.curr_wheel_text,  pos=(0,0), 
                  flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.curr_wheel,  pos=(0,1), 
                  flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.wheel_choice, pos=(1,0), 
                  flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.select_button, pos=(1,1), 
                  flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.home_button, pos=(1,2), 
                  flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
    
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(200, -1))
        boxSizer.Add(
            sizer, 
            flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizerAndFit(boxSizer)

    @run_async(daemon=True)
    def OnSelect(self, event):
        """Moves wheel to the selected position."""
        wx.CallAfter(self.Enable, False)
        selected = self.wheel_choice.GetSelection()
        if selected is -1:
            wx.CallAfter(wx.MessageBox,'Please select a position!', 
                         'NO POSITION SELECTED!', wx.OK | wx.ICON_ERROR)
            return
        try:
            self.wheel.move(selected)
            wx.CallAfter(self.curr_wheel.SetLabel, self.wheel.position)
        except InstrumentError:
            wx.CallAfter(self.curr_wheel.SetLabel, 'ERROR')
        finally:
            wx.CallAfter(self.Enable, True)

    @run_async(daemon=True)
    def OnHome(self, event):
        """Moves wheel to the home position."""
        wx.CallAfter(self.Enable, False)
        try:
            self.wheel.home()
            wx.CallAfter(self.curr_wheel.SetLabel, self.wheel.position)
        except InstrumentError:
            wx.CallAfter(self.curr_wheel.SetLabel, 'ERROR')
        finally:
            wx.CallAfter(self.Enable, True)
