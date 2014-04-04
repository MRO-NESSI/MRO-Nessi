import newport as np
from instrument.component import InstrumentComponent, InstrumentError, logCall

class DewarWheel(InstrumentComponent):
    """Represents a Newport controlled wheel in the dewar.

    Methods:
        home
        initialize
        kill
        move
    """

    def __init__(self, instrument, name, sockets, positions):
        """Connects to, initializes, and homes a specified wheel in 
        the dewar. 

        Arguments:
            instrument -- Copy of the NESSI instrument -> Instrument
            name       -- Name of the wheel to control -> str 
            sockets    -- List of integers representing TCP sockets ->[Int]
            positions  -- Possible positions for the wheel -> [str]
;
        Raises:
             InstrumentError
        """

        super(DewarWheel, self).__init__(instrument)
        
        self.instrument  = instrument
        self.name        = name
        self.controller  = instrument.newport
        self.sockets     = sockets
        self.home_pos    = 0
        self.current_pos = 0
        self.positions   = positions

        self.initialize()
        #self.home()

    def __str__(self):
        return self.name

    @property
    def position(self):
        """Returns the name of the current position."""

        return self.positions[self.current_pos]

    @logCall(msg='Moving Dewar Wheel.')
    def move(self, selected_pos):
        """Moves the wheel to a selected position.
            
        Arguments:
            selected_pos -- Which position to move to. -> int

        Raises:
            InstrumentError
        
        Returns:
            self.current_pos -- The current position of the wheel. -> int
        """
        try:
            with self.lock:
                self.current_pos = np.NewportWheelMove(self.controller, 
                                                   self.name, self.sockets[0],
                                                   self.current_pos, 
                                                   selected_pos)
                return self.current_pos

        except Exception as e:
            raise InstrumentError('An error occured during a movement of'
                                  ' the' + self.name + '\n The following '
                                  ' error was raised...\n %s' % repr(e))  

    @logCall(msg='Homeing Dewar Wheel.')
    def home(self):
        """Homes the wheel.
            
        Arguments:
            None

        Raises:
            InstrumentError

        Returns:
            None
        """
        try:
            with self.lock:
                np.NewportWheelHome(self.controller, 
                                                   self.name, self.sockets[0])
                self.current_pos = 0

        except Exception as e:
            raise InstrumentError('An error occured during a homing of'
                                  ' the' + self.name + '\n The following '
                                  ' error was raised...\n %s' % repr(e))       
    
    def kill(self):
        """Stops motion. Called by a kill_all.
            
        Arguments:
            None

        Raises:
            InstrumentError
        
        Returns:
            None
        """
        try:
            np.NewportKill(self.controller, self.name, self.sockets[1])

        except Exception as e:
            raise InstrumentError('An error occured during a kill sequence of'
                                  ' the' + self.name + '\n The following '
                                  ' error was raised...\n %s' % repr(e))

    def initialize(self):
        """Initializes the motor.
            
        Arguments:
            None

        Raises:
            InstrumentError
        
        Returns:
            None
        """
        try:
            with self.lock:
                np.NewportInitialize(self.controller, self.name,
                                     self.sockets[0], self.home_pos)
        #TODO: We shouldn't have a catchall here!
        except Exception as e:
            raise InstrumentError('An error occured during initialization of'
                                  ' the' + self.name + '\n The following '
                                  ' error was raised...\n %s' % repr(e))
