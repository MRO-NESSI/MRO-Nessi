import logging

import wx

from instrument.component import InstrumentError
from threadtools import run_async

class FocusREIPanel(wx.Panel):
    """This panel controls the position of REI1-2 """

    def __init__(self, parent, name, motor):
        """Builds a FocusREIPanel.

        Arguments:
            parent -- Parent panel.
            name   -- Name of the panel
            motor  -- thorlabs motor object.

        Raises:
            None
        """

        super(FocusREIPanel, self).__init__(parent) 
        
        self.parent = parent
        self.name   = name
        self.motor  = motor

        #Current Position
        ################################################################
        self.curr_pos_label = wx.StaticText(self, 
                                            label=u'Position \u03bc m:')
        self.curr_pos = wx.StaticText(self, label="...")
        
        #Goto Button
        ################################################################
        self.goto_button = wx.Button(self, label="Set", size=(50,-1))
        self.goto_value  = wx.TextCtrl(self, -1, '', size=(50,-1), 
                                      style=wx.TE_NO_VSCROLL)
        #In Button
        ################################################################
        self.in_button  = wx.Button(self, label=u'\u21e6 In', size=(50,-1))
        self.out_button = wx.Button(self, label="Out " + u'\u21e8', 
                                    size=(50,-1))
        
        #Step Size
        ################################################################
        self.step_size = wx.SpinCtrl(self, -1, '', (-1, -1),  (50, -1))
        self.step_size.SetRange(1, 1000)
        self.step_size.SetValue(0)
        
        #Layout
        ################################################################
        self.__DoLayout()
        
        # Event Handlers
        ################################################################
        self.out_button.Bind(wx.EVT_BUTTON, self.onOut)
        self.in_button.Bind(wx.EVT_BUTTON, self.onIn)
        self.goto_button.Bind(wx.EVT_BUTTON, self.onGoto)

        #Decide if the device should be active
        ################################################################
        if self.motor is None:
            self.Enable(False)

    def __DoLayout(self):
        sbox = wx.StaticBox(self, label=self.name)
        boxSizer = wx.StaticBoxSizer(sbox, wx.HORIZONTAL)

        sizer = wx.GridBagSizer(vgap=2, hgap=2)

        sizer.Add(self.curr_pos_label,  pos=(0,0), span=(1,2), 
                  flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.curr_pos,  pos=(0,2), span=(1,2), 
                  flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
        
        sizer.Add(self.goto_button, pos=(1,0), span=(1,2), 
                  flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.goto_value, pos=(1,2), span=(1,2), 
                  flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
    
        sizer.Add(self.in_button, pos=(2,0), 
                  flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.step_size, pos=(2,1), span=(1,2), 
                  flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.out_button, pos=(2,3), 
                  flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        
        # Add the grid bag to the static box and make everything fit
        sizer.SetMinSize(wx.Size(150, -1))

        boxSizer.Add(
            sizer,flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizerAndFit(boxSizer)

    @run_async(daemon=True)
    def onOut(self, event):
        #Disable frame
        ################################################################
        wx.CallAfter(self.curr_pos.SetLabel, '...')
        wx.CallAfter(self.Enable, False)

        step = self.step_size.GetValue() 

        #Move motor
        ################################################################
        try:
            self.motor.move_relative(step)
        except:
            wx.CallAfter(self.curr_pos.SetLabel,
                         'ERROR!')
            return
    
        #Enable frame
        ################################################################
        self.updateCurrPos()
        wx.CallAfter(self.Enable, True)            
            


    @run_async(daemon=True)
    def onIn(self, event):
        #Disable frame
        ################################################################
        wx.CallAfter(self.curr_pos.SetLabel, '...')
        wx.CallAfter(self.Enable, False)

        step = self.step_size.GetValue() 

        #Move motor
        ################################################################
        try:
            self.motor.move_relative(-1*step)
        except InstrumentError:
            wx.CallAfter(self.curr_pos.SetLabel,
                         'ERROR!')
            return

        #Enable frame
        ################################################################
        self.updateCurrPos()
        wx.CallAfter(self.Enable, True)
    
    @run_async(daemon=True)
    def onGoto(self, event):
        #Disable frame
        ################################################################
        wx.CallAfter(self.curr_pos.SetLabel, '...')
        wx.CallAfter(self.Enable, False)


        try:
            #Get desired location
            ################################################################
            loc = self.goto_value.GetValue()
            loc = float(loc)

            #Move motor
            ################################################################
            self.motor.move_absolute(loc)        

        except InstrumentError:
            wx.CallAfter(self.curr_pos.SetLabel,
                         'ERROR!')
            return
        
        except ValueError:
            wx.CallAfter(wx.MessageBox,'Please select a valid number!', 
                         'INVALID FOCUS POSITION!', wx.OK | wx.ICON_ERROR)

        #Enable frame
        ################################################################
        self.updateCurrPos()
        wx.CallAfter(self.Enable, True)

    def updateCurrPos(self):
        try:
            wx.CallAfter(self.curr_pos.SetLabel, 
                         '%.3f' % self.motor.position)
        except InstrumentError:
            wx.CallAfter(self.curr_pos.SetLabel,
                         'ERROR!')
            return            

