p#!/usr/bin/env python
"""
 Control software for NESSI
 
 author:       Luke Schmidt, Matt Napolitano, Tyler Cecil
 author_email: lschmidt@nmt.edu
"""

__author__ = 'Luke Schmidt, Matt Napolitano, Tyler Cecil'
__date__   = '2013'

import logging
from logging.handlers import TimedRotatingFileHandler
from os import makedirs, execl
from os.path import isdir, join
import signal
import sys
import SocketServer
import traceback

from configobj import ConfigObj
import ds9
import wxversion
wxversion.select('2.8')
import wx
from wx.lib.agw import advancedsplash 

from gui.gui import MainNessiFrame
from instrument.instrument import Instrument
from gui.logtab.log import wxLogHandler, EVT_WX_LOG_EVENT
from threadtools import run_async, shutdown

CONFIG_PATH        = 'nessisettings.ini'
SPLASH_BITMAP_PATH = 'media/badass.png'
HOST               = 'localhost'
PORT               = 8989

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
    splash, splashHandler = buildSplash(SPLASH_BITMAP_PATH)
    
    #Build configure object
    ################################################################
    cfg = ConfigObj(CONFIG_PATH)

    #SIGABRT Handler setup (signaled by a "shutdown")
    ################################################################
    def shutdownHandler(signum, frame):
        logging.info("Shutting Down...")

        #close DS9
        try:
            for d in ds9.ds9_openlist():
                d.set('exit')
        except ValueError:
            pass
        
        app.Destroy()
        self.socket.shutdown()
        try:
            instrument.closeTelescope()
        finally:
            exit(0)

    signal.signal(signal.SIGABRT, shutdownHandler)

    #SIGINT Handler setup (signaled by a "kill all" or keyboard.)
    ################################################################
    def sigintHandler(signum, frame):
        #instrument.kill_all()
        try:
            instrument.closeTelescope()
        except:
            dlg = wx.MessageDialog(None, 'instrument.closeTelescope() failed!'
                                   ' Report to someone who writes software!',
                                   '!!!KILL ALL --- Telescope Close Failed!!!',
                                   wx.YES_NO | wx.ICON_QUESTION)

        dlg = wx.MessageDialog(None, 'A KILLALL has been raised!\n'
                               ' Would you like to restart the program?',
                               '!!!KILL ALL!!!',
                               wx.YES_NO | wx.ICON_QUESTION)
        restart = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        
        if restart:
            app.Destroy()

            selfpid = sys.executable
            execl(selfpid, selfpid, * sys.argv)
        else:
            shutdown()

    signal.signal(signal.SIGINT, sigintHandler)

    #SIGPOLL Will force python to write FITS headers to a FIFO
    #So that OWL may use it
    ################################################################
    def sigpollHandler(signum, frame):
        #Not that keywords will attempt to read components that
        #may be locked. Instrument must be "idle" for this to work
        #without delay.
        mkfifo('fitsFifo')

        fitsKeywords = instrument.keywords

        f = open('fitsFifo', 'w')
        f.write(str(fitsKeywords))
        f.close()
    
    signal.signal(signal.SIGPOLL, sigpollHandler)

    #Socket Server for sending keywords
    ################################################################
    class KeywordTCPHandler(SocketServer.StreamRequestHandler):
        def handle(self):
            logging.info("Dumping keywords to stream socket...")

            keywords = instrument.keywordsH2RG
            for key in keywords:
                self.wfile.write("%s\t%s\n" % (key, keywords[key]))

            logging.info("Socket closing...")

    server = SocketServer.TCPServer((HOST, PORT), KeywordTCPHandler)
    
    @run_async(daemon=True)
    def startServer():
        server.serve_forever()
    
    startServer()
        

    #Build Instrument
    ################################################################
    instrument = buildInstrument(cfg)
    
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


def buildInstrument(cfg):
    """Given a config object, construct the instrument.
    This will give the user a graphic way to handle initialization
    errors, as well.

    Arguments:
        cfg - ConfigObj
    Returns:
        instrument object
    """

    #Build instrument
    ################################################################
    try:
        instrument = Instrument(cfg)
    except Exception as e:
        wx.MessageBox('An unknown error was raised during the'
                      ' initialization of the instrument. See log'
                      ' for details. NESSI will shut down.', 
                      'UNKNOWN INITIALIZATION ERROR!', 
                      wx.OK | wx.ICON_ERROR)
        logging.critical(traceback.format_exc())
        shutdown()

    #Check for components that did not initialize
    ################################################################
    failedComponents = [compName for compName, comp in 
                        instrument.components.items() if comp == None]
    
    if failedComponents:
        dlg = wx.MessageDialog(None, 'The following instrument components'
                               ' did not initialize: ' + str(failedComponents) + '\n'
                               'Would you like to continue anyway?',
                               'Instrument Partially Initialized!',
                               wx.YES_NO | wx.ICON_QUESTION)
        moveon = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        
        if not moveon:
            shutdown()

    #Connect to telescope
    ################################################################
    try:
        #instrument.connectTelescope()
        pass
    except:
        wx.MessageBox('Unable to connect to telescope! NESSI must shut'
                      ' down!', 'TELESCOPE CONNECTION ERROR!',
                      wx.OK | wx.ICON_ERROR)
        logging.critical(traceback.format_exec())
        shutdown()

    return instrument


    
def buildSplash(image_dir):
    """Make a splash page to display logging info.
    Will also initialize the logger to print to splash
    page.

    Note: The splash page does not appear to update it's
    text, unless a message box comes up. This needs to be
    looked into.
    
    Arguments:
        image_dir -- Path to the image of the splash screen.
    Raises:
        None
    Returns
        (A splash screen, splashHandler) ([AdvancedSplash], [wxLogHandler])
    """

    bitmap = wx.Bitmap(image_dir, wx.BITMAP_TYPE_PNG)
    splash = advancedsplash.AdvancedSplash(
        None, bitmap = bitmap, timeout=0,
        agwStyle = advancedsplash.AS_NOTIMEOUT | 
        advancedsplash.AS_CENTER_ON_SCREEN)
    splash.SetText('NESSI initializing...')

    #Splash logger
    ################################################################
    def onLogEvent(event):
        msg = event.message.strip('\r') + '\n'
        wx.CallAfter(splash.SetText,msg)
        wx.Yield()
        event.Skip()

    splashHandler = wxLogHandler(splash)
    splashHandler.setLevel(logging.INFO)
    logging.getLogger('').addHandler(splashHandler)

    splash.Bind(EVT_WX_LOG_EVENT, onLogEvent)

    return splash, splashHandler


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
    main()
