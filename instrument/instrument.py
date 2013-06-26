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
        
        #Define list of actuators
        ################################################################
        self.newport       = None
        self.kmiror        = None
        self.mask_wheel    = None
        self.filter1_wheel = None
        self.filter2_wheel = None
        self.grism_wheel   = None
        self.guide_focus   = None
        self.REI34_focus   = None

        self.actuators = [
            self.newport      ,
            self.kmiror       ,
            self.mask_wheel   ,
            self.filter1_wheel,
            self.filter2_wheel,
            self.grism_wheel  ,
            self.guide_focus  ,
            self.REI34_focus  ,
            ]

        #Define list of sensors
        ################################################################
        self.temperature = None
        self.guide_cam   = None

        self.sensors = [
            self.temperature ,
            self.guide_cam   ,
            ]

        #Define keywords
        ################################################################
        keywords = {"OBSERVER"  : "Observer",
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

        #Build component list
        ################################################################
        self.components = self.actuators + self.sensors

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
        #TODO: Implement!
        pass
        
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

        arguments:
        msg -- Message that will be tied to the KillAllException,
               explaining why the kill was called.

        returns None
        """
        #TODO: Implement!
        pass

    def move_telescope(self, ra, dec):
        """Will move the telescope to a new RA and DEC.

        arguments:
        ra  -- New right ascension
        dec -- New declination

        returns None
        """
        #TODO: Implement!
        pass


