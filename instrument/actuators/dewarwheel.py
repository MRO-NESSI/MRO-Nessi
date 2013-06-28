import newport as np
from instrument import InstrumentComponent, InstrumentError

class DewarWheel(InstrumentComponent):
    """Represents a Newport controlled wheel in the dewar.

    Methods:
        Home
        Initialize
        Kill
        Move
    """

    def __init__(self, instrument, wheel, controller, sockets):
        """Connects to, initializes, and homes a specified wheel in the dewar. 

        Arguments:
            instrument -- Copy of the NESSI instrument
            wheel      -- Name of the wheel to control [str] 
            controller -- XPS instance to use for control 
            sockets    -- List of integers representing TCP sockets

        Raises:
             InstrumentError
        
        Returns:
            None
        """

        super(DewarWheel, self).__init__(instrument)
        
        self.motor = wheel
        self.controller = controller
        self.sockets = sockets
        self.home_pos = 0
        self.current_pos = None
        self.selected_pos = None

        self.Initialize()
        self.Home()

    def Move(self, self.selected_pos):
        """Moves the wheel to a selected position.
            
        Arguments:
            self.selected_pos -- Which position [int] to move to.

        Raises:
            InstrumentError
        
        Returns:
            self.current_pos -- The current [int] position of the wheel. 
        """
        try:
            with self.lock:
                self.current_pos = np.NewportWheel(self.controller, 
                                                   self.motor, self.sockets[0],
                                                   self.current_pos, 
                                                   self.selected_pos, False)
                return self.current_pos

        except Exception e:
            raise InstrumentError('An error occured during a movement of'
                                  ' the' + self.motor + '\n The following '
                                  ' error was raised...\n %s' % repr(e))  

    def Home(self):
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
                self.current_pos = np.NewportWheel(self.controller, 
                                                   self.motor, self.sockets[0],
                                                   0, 0, True)

        except Exception e:
            raise InstrumentError('An error occured during a homing of'
                                  ' the' + self.motor + '\n The following '
                                  ' error was raised...\n %s' % repr(e))       
    
    def Kill(self):
        """Stops motion. Called by a kill_all.
            
        Arguments:
            None

        Raises:
            InstrumentError
        
        Returns:
            None
        """
        try;
            np.Kill(self.controller, self.motor, self.sockets[1])

        except Exception e:
            raise InstrumentError('An error occured during a kill sequence of'
                                  ' the' + self.motor + '\n The following '
                                  ' error was raised...\n %s' % repr(e))

    def Initialize(self):
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
                np.NewportInitialize(self.controller, self.motor,
                                     self.sockets[0], self.home_pos)

        except Exception e:
            raise InstrumentError('An error occured during initialization of'
                                  ' the' + self.motor + '\n The following '
                                  ' error was raised...\n %s' % repr(e))
