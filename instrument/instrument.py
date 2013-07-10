import logging
import sys

from configobj import ConfigObj

from   actuators.dewarwheel import DewarWheel
from   actuators.kmirror    import KMirror
from   actuators.thorlabs   import ThorlabsController
import actuators.XPS_C8_drivers as xps
from   component            import InstrumentError, KillAllError
from   sensors.lakeshore    import LakeshoreController
from   sensors.flicam       import FLICam
from   threadtools          import timeout, TimeoutError

sockets = 40

class Instrument(object):
    """Class to represent the NESSI instrument.
       
    Keeps a list of all actuators and sensors. It will provide a
    valid list of keywords to be used for FITS headers. It also 
    will provide a tidy way to initialize and/or close all 
    connections.
    
    This object alone should suffice to control NESSI entirely.
    """
    
    def __init__(self, ):
        """Initialize the NESSI instrument.
        
        Those components which cannot initialize will become None,
        and an error will be logged acordingly. This will not exit
        program, however. It is the duty of external interfaces to
        check whether or not their respective components are None.
        """

        #Config object
        ################################################################
        self.cfg = ConfigObj('nessisettings.ini')
        
        #Define list of actuators
        ################################################################
        #Newport things
        self.newport       = None
        self.open_sockets  = None
        self.kmiror        = None        
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

        #Define keywords
        ################################################################
        #TODO: Be sure to be getting decimal degrees
        self.keywords = {
            "OBSERVER"  : "Observer",
            "INST"      : "NESSI",
            "TELESCOP"  : "MRO 2.4m",
            "FILENAME"  : "default",
            "IMGTYPE"   : "imgtyp",
            "RA"        : "TCS down" ,   
            "DEC"       : "TCS down",  
            "AIRMASS"   : "TCS down",       
            "TELALT"    : "TCS down",
            "TELAZ"     : "TCS down",
            "TELFOCUS"  : "TCS down",
            "PA"        : "TCS down",
            "JD"        : "TCS down",
            "GDATE"     : "TCS down",
            "WINDVEL"   : "No Env data",
            "WINDGUST"  : "No Env data",
            "WINDDIR"   : "No Env data",
            "REI12"     : 0.0, # focus position
            "REI34"     : 0.0, # focus position
            "MASK"      : "None",
            "FILTER1"   : "None",
            "FILTER2"   : "None",
            "GRISM"     : "None",
            "EXP"       : 0.0,
            "CAMTEMP"   : 0.0,
            "CTYPE1"    : "RA---TAN",
            "CTYPE2"    : "DEC--TAN",
            "CRPIX1"    : 512.0,
            "CRPIX2"    : 512.0,
            "CDELT1"    : 0.0, 
            "CDELT2"    : 0.0,
            "CRVAL1"    : 0.0, 
            "CRVAL2"    : 0.0,
            "CROTA2"    : 0.0
            }

        #Init components
        ################################################################
        self._init_components()

        #Get Telescope data
        ################################################################
        self.update_telescope_data()

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
            raise InstrumentInitializationError(
                'Newport sockets could not be filled!')

        if newport_good:
            #Kmirror
            ################
            try:
                self.kmiror        = KMirror(self, self.newport, 
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
        
    @property
    def actuators(self):
        actuators = [
            self.newport      ,
            self.kmiror       ,
            self.mask_wheel   ,
            self.filter1_wheel,
            self.filter2_wheel,
            self.grism_wheel  ,
            self.guide_focus  ,
            self.REI34_focus  ,
            ]
        return actuators

    @property
    def sensors(self):
        sensors = [
            self.temperature ,
            self.guide_cam   ,
            ]
        return sensors

    @property
    def components(self):
        return self.actuators + self.sensors
        
    @timeout(20)
    def _fill_socket_list(self):
        for i in range(40):
            self.open_sockets.append(
                self.newport.TCP_ConnectToServer('192.168.0.254',5001,1))
        
        # Checking the status of the connections.
        for i in range(40):
            if self.open_sockets[i] == -1:
                raise InstrumentError('Newport socket connection not opened'
                                      ' at position ' + str(i))
    
    @timeout(10)
    def _close_sockets(self):
        for i in range(len(self.open_sockets)):
            self.newport.TCP_CloseSocket(self.open_sockets[i])            
        
    def update_telescope_data(self):
        """Will communicate with the telescope via indiclient
        and fetch the indivectors that are relevant to us.
        It will the put this information into the keywords
        dictionary.

        returns None
         """
        #TODO: Implement!
        pass

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

        raise KillAllError(msg)

    def move_telescope(self, ra, dec):
        """Will move the telescope to a new RA and DEC.

        Arguments:
            ra  -- New right ascension
            dec -- New declination

        returns None
        """
        #TODO: Implement!
        pass

    def __del__(self):
        self.kill_all('Instrument is being deleted.')


class InstrumentInitializationError(InstrumentError):
    pass
