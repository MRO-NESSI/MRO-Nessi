#!/usr/bin/env python
"""
 Control software for NESSI
 
 author:       Luke Schmidt, Matt Napolitano, Tyler Cecil
 author_email: lschmidt@nmt.edu
"""

__author__ = 'Luke Schmidt, Matt Napolitano, Tyler Cecil'
__date__ = '2013'

import logging
from logging.handlers import TimedRotatingFileHandler
from os import makedirs
from os.path import isdir, join
import sys
import traceback

from configobj import ConfigObj
import wxversion
wxversion.select('2.8')
import wx
from wx.lib.agw import advancedsplash 

from gui.gui import MainNessiFrame
from instrument.instrument import Instrument
from gui.logtab.log import wxLogHandler, EVT_WX_LOG_EVENT

def main(argv=None):
    """Run the entirety of the nessi software.

    Arguments:
        argv -- Sys args. Not currently used.
    Raises:
        None
    Returns:
        None
    """
    
    #Init wx App
    ################################################################
    app = wx.App()

    #Add nessi package to path
    ################################################################
    sys.path.append("./")

    #Init Logger
    ################################################################
    initLogger()

    #Set up splash page
    ################################################################
    splash = buildSplash('media/badass.png')

    #Splash logger
    def onLogEvent(event):
        msg = event.message.strip('\r') + '\n'
        wx.CallAfter(splash.SetText,msg)
        wx.Yield()
        event.Skip()

    splashHandler = wxLogHandler(splash)
    splashHandler.setLevel(logging.INFO)
    logging.getLogger('').addHandler(splashHandler)

    splash.Bind(EVT_WX_LOG_EVENT, onLogEvent)

    #Build configure object
    ################################################################
    cfg = ConfigObj('nessisettings.ini')

    #Build instrument
    ################################################################
    try:
        instrument = Instrument()
    except Exception as e:
        wx.MessageBox('An unknown error was raised during the'
                      ' initialization of the instrument. See log'
                      ' for details. NESSI will shut down.', 
                      'UNKNOWN INITIALIZATION ERROR!', 
                      wx.OK | wx.ICON_ERROR)
        logging.critical(traceback.format_exc())
        app.Destroy()

        #TODO: Raise SIGABT
        return

    #Make main frame
    ################################################################
    frame = MainNessiFrame(instrument)

    #Kill splash
    ################################################################
    logging.getLogger('').removeHandler(splashHandler)
    splash.Destroy()

    #Start App
    ################################################################
    frame.Show()
    app.MainLoop()

    
def buildSplash(image_dir):
    """Make a splash page to display logging info.
    
    Arguments:
        image_dir -- Path to the image of the splash screen.
    Raises:
        None
    Returns
        A splash screen [AdvancedSplash]
    """

    bitmap = wx.Bitmap(image_dir, wx.BITMAP_TYPE_PNG)
    splash = advancedsplash.AdvancedSplash(
        None, bitmap = bitmap, timeout=0,
        agwStyle = advancedsplash.AS_NOTIMEOUT | 
        advancedsplash.AS_CENTER_ON_SCREEN)
    splash.SetText('NESSI initializing...')
    return splash


def initLogger(level=logging.DEBUG, logdir='logfiles'):
    """Sets the desired settings for the logger
    
    Arguments:
        level  -- Level to set the root logger at. Take
                  from logging.DEBUG/logging.INFO/ect...
        logdir -- Directory to put log files.
    Returns:
        None
    """

    #Check if logdir exists. Make if not.
    ################################################################
    if not isdir(logdir): makedirs(logdir)

    #Init Logger
    ################################################################
    logging.basicConfig(level=level)
    logfileHandler = TimedRotatingFileHandler(join(logdir, 'NESSILog'),
                                              when='d')
    logfileFormatter = logging.Formatter(
        '[%(asctime)s] %(filename)s:%(funcName)s - %(message)s')
    logfileHandler.setLevel(level)    
    logfileHandler.setFormatter(logfileFormatter)

    logging.getLogger('').addHandler(logfileHandler)
                        
if __name__ == "__main__":
#    try:
    main()
#    except KeyboardInterrupt:
#        wx.MessageBox('Are you ok?', 
#                      'KILL ALL RAISED!', wx.YES_NO | wx.ICON_ERROR)

