"""
.. module:: instrument
   :platform: Unix
   :synopsis: The main file to interface with the NESSI instrument.
   
.. moduleauthor:: Tyler Cecil <tcecil@mro.nmt.edu>

"""

import logging
import sys
import os
#os.environ["NUMERIX"] = "numarray" # make pyfits use numarray

from configobj import ConfigObj
#import numarray as num
import pyfits
import pywcs
import PyGuide

from   actuators.dewarwheel import DewarWheel
from   actuators.kmirror    import KMirror
from   actuators.thorlabs   import ThorlabsController
import actuators.XPS_C8_drivers as xps
from   component            import InstrumentError, KillAllError
from   sensors.lakeshore    import LakeshoreController
from   sensors.flicam       import FLICam
from   threadtools          import timeout, TimeoutError
from   telescope.telescope  import Telescope

class Instrument(object):
    """Class to represent the NESSI instrument.
       
    Keeps a list of all actuators and sensors. It will provide a
    valid list of keywords to be used for FITS headers. It also 
    will provide a tidy way to initialize and/or close all 
    connections.
    
    Every component will be an instance of `instrument.component.Component`.

    This object alone should suffice to control NESSI entirely.

    Attributes
    ----------
    cfg : ConfigObj
        Configuration object.
    newport : xps Object
        Newport XPS controller.
    open_sockets : [int]
        List of open Newport Sockets.
    kmirror : KMirror Object
        Kmirro interface.
    mask_wheel : DewarWheel
        Mask Wheel interface.
    filter1_wheel : DewarWheel
        Filter 1 Wheel interface.
    filter2_wheel : DewarWheel
        Filter 2 Wheel interface.
    grism_wheel : DewarWheel
    guide_focus : ThorlabsController
        Focus ring for Guide Camera interface.
    REI34_focus : ThorlabsController
        Focus rings for REI 3/4 interface.
    temperature : LakeshoreController
        Temperature sensor interface.
    guide_cam : FLICam
        Guide camera interface.

    Methods
    -------
    update_telescope_data()
        Reads in the telescope position, updates ra and dec.
    def kill_all(msg=None)
        Safely disconnects all instrument components
    def move_telescope(ra, dec)
        Move the telescope.
     
    """

    _sockets = 40

    def __init__(self, cfg):
        """Initialize the NESSI instrument.
        
        Those components which cannot initialize will become None,
        and an error will be logged acordingly. This will not exit
        program, however. It is the duty of external interfaces to
        check whether or not their respective components are None.
        """

        #Config object
        ################################################################
        self.cfg = cfg
        
        #Define list of actuators
        ################################################################
        #Newport things
        self.newport       = None
        self.open_sockets  = None
        self.kmirror       = None        
        self.mask_wheel    = None
        self.filter1_wheel = None
        self.filter2_wheel = None
        self.grism_wheel   = None

        self.guide_focus   = None
        self.REI34_focus   = None

        #Define list of sensors
        ################################################################
        self.temperature = None
        self.guide_cam   = None

        #Define telescope
        ################################################################
        self.telescope = None

        #Init components
        ################################################################
        self._init_components()


    def connectTelescope(self):
        try:
            self.telescope = Telescope('192.168.0.5', 7624)
        except:
            raise InstrumentError('Unable to connect to telescope!')

    def closeTelescope(self):
        if isinstance(self.telescope, Telescope):
            self.telescope._indi.quit()

    def _init_components(self):
        """Initialize the instrument components and connections. Logs
        errors as they occur, but will never halt or abort the program.
        """
        #TODO: Finish Implement!

        #Initialize newport components.
        ################################################################
        #This is the only init step that may cause an
        #InstrumentInitializationError.
        #In the case of test, this error should be caught, and objects
        #should handle the case when these components are none.

        newport_good = False    #Flag for if the newport was initialized

        self.newport = xps.XPS()
        self.open_sockets=[]
        logging.debug('Newport initialized!')

        #Fill Sockets
        ################################################################
        try:
            self._fill_socket_list()
            logging.debug('Sockets filled!')
            newport_good = True
        except TimeoutError:
            logging.debug('Newport Sockets timed out!')
            sys.exc_clear()
        except InstrumentError:
            logging.debug('Newport errored out initializing sockets!')
            sys.exc_clear()



        if newport_good:
            #Kmirror
            ################
            try:
                self.kmirror        = KMirror(self, self.newport, 
                                             self.open_sockets[20:])
                logging.debug('K-Mirror initialized!')
            except InstrumentError:
                sys.exc_clear()


            #Mask
            #################
            try:
                self.mask_wheel    = DewarWheel(self, 'mask',
                                                self.open_sockets[0:4],
                                                self.cfg['mask']['pos'])
                logging.debug('Mask wheel initialized!')
            except InstrumentError:
                sys.exc_clear()
            
            #Filter 1
            ################
            try:
                self.filter1_wheel = DewarWheel(self, 'filter1',
                                                self.open_sockets[5:9],
                                                self.cfg['filter1']['pos'])
                logging.debug('Filter1 wheel initialized!')
            except InstrumentError:
                sys.exc_clear()

            #Filter 2
            ################
            try:
                self.filter2_wheel = DewarWheel(self, 'filter2',
                                                self.open_sockets[10:14],
                                                self.cfg['filter2']['pos'])
                logging.debug('Filter2 wheel initialized!')
            except InstrumentError:
                sys.exc_clear()

            #Grism
            ################
            try:
                self.grism_wheel   = DewarWheel(self, 'grism',
                                                self.open_sockets[15:19],
                                                self.cfg['grism']['pos'])
                logging.debug('Grism wheel initialized!')
            except InstrumentError:
                sys.exc_clear()

                
        #Thorlabs components
        ################################################################
        try:
            self.REI34_focus = ThorlabsController(self, 0)
        except InstrumentError:
            sys.exc_clear()

        try:
            self.guide_focus = ThorlabsController(self, 1)
        except InstrumentError:
            sys.exc_clear()

            
        #Sensors
        ################################################################
        try:
            self.temperature = LakeshoreController(self)
        except InstrumentError:
            sys.exc_clear()

        try:
            self.guide_cam = FLICam(self)
        except InstrumentError:
            sys.exc_clear()

        #Connect to Telescope
        ################################################################
        try:
            self.connectTelescope()
        except InstrumentError:
            sys.exc_clear()



    @property
    def keywords(self):
        #Define keywords
        ################################################################
        #TODO: Be sure to be getting decimal degrees
        keywords = {
            "OBSERVER" : "Observer",    #TODO: Get from somewhere
            "INST"     : "NESSI",       
            "TELESCOP" : "MRO 2.4m",    #TODO:Get from indi?
            "FILENAME" : "default",     #TODO:Do these later?
            "IMGTYPE"  : "imgtyp",      
            "RA"       : 
            self.telescope.ra if self.telescope else None,
            "DEC"      : 
            self.telescope.dec if self.telescope else None,
            "AIRMASS"  : 
            self.telescope.airmass if self.telescope else None,
            "TELALT"   : 
            self.telescope.altitude if self.telescope else None,
            "TELAZ"    : 
            self.telescope.azimuth if self.telescope else None,
            "TELFOCUS" : "TCS down",    #TODO:Where is?
            "PA"       : 
            self.telescope.parallactic_angle if self.telescope else None,
            "JD"       : 
            self.telescope.julian_date if self.telescope else None,
            "GDATE"    : "TCS down",    #TODO:Generate
            #"WINDVEL"  : self.telescope.wind_speed,
            #"WINDGUST" : self.telescope.wind_gust,
            #"WINDDIR"  : self.telescope.wind_direction,
            "AGR"      : 0.0,           #focus position ???
            "REI34"    : 0.0,           #focus position (Dewar focus)
            "MASK"     : 
            self.mask_wheel.position if self.mask_wheel else None,
            "FILTER1"  : 
            self.filter1_wheel.position if self.filter1_wheel else None,
            "FILTER2"  : 
            self.filter2_wheel.position if self.filter2_wheel else None,
            "GRISM"    : 
            self.grism_wheel.position if self.grism_wheel else None,
            "EXP"      : 0.0,           #??????????
            "CAMTEMP"  : 
            self.guide_cam.getTemperature() if self.guide_cam else None,
            "CTYPE1"   : "RA---TAN",    #?????????
            "CTYPE2"   : "DEC--TAN",    #?????????
            #The following two values are for the guide cam. They
            #are overwritten in main.py KeywordTCPHandler for the
            #H2RG
            "CRPIX1"   : 528.0,         # ref point pixel x
            "CRPIX2"   : 513.5,         # ref point pixel y
            "CDELT1"   : 0.000119444444,# deg per pixel x
            "CDELT2"   : 0.000119444444,# deg per pixel y
            "CRVAL1"   : 0.0,           #?????????
            "CRVAL2"   : 0.0,           #?????????
            "CROTA2"   : 0.0            #?????????
            }
        
        return keywords

    @property
    def actuators(self):
        actuators = {
            'kmirror'        : self.kmirror      ,
            'Mask Wheel'     : self.mask_wheel   ,
            'Filter 1 Wheel' : self.filter1_wheel,
            'Filter 2 Wheel' : self.filter2_wheel,
            'Grism Wheel'    : self.grism_wheel  ,
            'Guide Focus'    : self.guide_focus  ,
            'REI34 Focus'    : self.REI34_focus  ,
            }
        return actuators

    @property
    def sensors(self):
        sensors = {
            'Temperature Sensor' : self.temperature ,
            'Guide Cam'          : self.guide_cam   ,
            }
        return sensors

    @property
    def components(self):
        dictionary              = dict(self.actuators, **self.sensors)
        dictionary['Telescope'] = self.telescope
        return dictionary
        
    @timeout(10)
    def _fill_socket_list(self):
        for i in range(40):
            socket = self.newport.TCP_ConnectToServer(
                '10.90.20.1',5001,1)
            if socket is not -1:
                self.open_sockets.append(socket)
            else:
                raise InstrumentError('Newport socket connection not opened'
                                      ' at position %d!' % i)
    
    @timeout(10)
    def _close_sockets(self):
        for i in range(len(self.open_sockets)):
            self.newport.TCP_CloseSocket(self.open_sockets[i])            
        

    def kill_all(self, msg=None):
        """Will call the kill function on all components and delete their
        references in parallel. Will then raise a KillAllException, which
        can be caught upstream if the program wishes to reinitialize the
        instrument.

        Arguments:
            msg -- Message that will be tied to the KillAllError,
                   explaining why the kill was called.

        returns None
        """
        #TODO: Implement!
        print msg
        pass

    def get_centroid(self, fits_image, initialxy):
        """Given a fits image, will return a centroid using
        PyGuid.Centroid.centroid. Will raise an error if the
        centroid is not ok.

        Arguments
        ---------
        fits_image --- a fits image (probably returned from the cam)
        intitialxy --- That thing.
        
        Returns
        -------
        PyGuid.Centroid object
        
        Raises
        ------
        Instrument Error
        """
        mask     = None
        satMask  = None
        rad      = 15
        ccdInfo  = PyGuide.CCDInfo(100.0, 12.5, 1.5, 65535)

        data     = fits_image[0].data
        centroid = PyGuide.Centroid.centroid(data, mask, satMask, 
                                             initialxy, rad, ccdInfo)
        
        if not centroid.isOK:
            raise InstrumentError("Centroid could not be found!")

        return centroid

    def calc_xy_shift(self, t0_centroid, tn_centroid, fits_header):
        """Given two PyGuid.Centroid objects, calculates the
        xy shift between the two, as Fortran-like sky coordinates

        Arguments
        ---------
        t0_centroid --- Centroid of t=0
        tn_centroid --- Centroid of t=1
        fits_header --- FITS header for tn_centroid

        Returns
        -------
        sky coordinates
        """
        #TODO: USE CRPIX IN THE KEYWORDS
        center_x = 528.0
        center_x = 513.5

        shift    = pixelmath.xy_move(t0_centroid, tn_centroid)
        wcs      = pywcs.WCS(fits_header)
        pixcrd   = np.array([[center_x+shift[0][0],center_y+shift[0][1]]], 
                              np.float_)

        sky    = wcs.wcs_pix2sky(pixcrd, 1)
        return sky

class InstrumentInitializationError(InstrumentError):
    pass
