import logging
from threading import Lock

class InstrumentComponent(object):
    """Abstract component to the NESSI instrument.

    Attributes:
        lock       -- Thread lock for the object. Most components 
                      interface with some form of hardware, so 
                      synchronization becomes important.
        instrument -- Copy of the instrument.
        
    """
    
    def __init__(self, instrument):
        """Build new InstrumentComponent, and build a lock for the
        component.
        
        Arguments:
           instrument -- copy of the NESSI instrument.
        """
        self.lock       = Lock()
        self.instrument = instrument
        
    def kill(self):
        """Called by a kill_all."""
        pass

class InstrumentError(Exception):
    """Base class for all exception that occur in the instrument.
    
    Attributes:
        msg -- High level explanation of the error. Should help
               a non-programmer fix the problem.
    """
    
    def __init__(self, msg):
        self.msg = msg
        logging.error(msg)

class KillAllError(InstrumentError):
    """Error raised when kill all is called. Raised so that the
    program can decide whether to abort or reinitialize.

    Attributes:
        msg -- explanation of why kill occurred
    """

    def __init__(self, msg):
        self.msg = msg
