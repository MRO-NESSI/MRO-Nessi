import functools
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
        logging.critical(msg)

class logCall(object):
    """Will log the function call with descriptor message"""


    def __init__(self, msg=None, logger=None):
        self.ENTRY_MESSAGE = 'BEGINNING: %s' % msg
        self.EXIT_MESSAGE  = 'FINISHED: %s'  % msg
        self.logger = logging if logger is None else logger
        
    def __call__(self, func):
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.ENTRY_MESSAGE += '\n\t Function Call: ' 
            self.ENTRY_MESSAGE += func.__name__ + str(args)
            self.ENTRY_MESSAGE += '\n\t Keyword Arguments: '
            self.ENTRY_MESSAGE += str(kwargs)
            self.logger.info(self.ENTRY_MESSAGE)

            result = func(*args, **kwargs)

            self.logger.info(self.EXIT_MESSAGE)

            return result

        return wrapper
