import newport as np
from instrument.component import InstrumentComponent, InstrumentError

class DewarWheel(InstrumentComponent):
    """Represents a Newport controlled wheel in the dewar.

    Methods:
        home
        initialize
        kill
        move
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

        self.initialize()
        self.home()

    def move(self, selected_pos):
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
                                                   selected_pos, False)
                return self.current_pos

        except Exception as e:
            raise InstrumentError('An error occured during a movement of'
                                  ' the' + self.motor + '\n The following '
                                  ' error was raised...\n %s' % repr(e))  

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
                self.current_pos = np.NewportWheel(self.controller, 
                                                   self.motor, self.sockets[0],
                                                   0, 0, True)

        except Exception as e:
            raise InstrumentError('An error occured during a homing of'
                                  ' the' + self.motor + '\n The following '
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
            np.Kill(self.controller, self.motor, self.sockets[1])

        except Exception as e:
            raise InstrumentError('An error occured during a kill sequence of'
                                  ' the' + self.motor + '\n The following '
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
                np.NewportInitialize(self.controller, self.motor,
                                     self.sockets[0], self.home_pos)

        except Exception as e:
            raise InstrumentError('An error occured during initialization of'
                                  ' the' + self.motor + '\n The following '
                                  ' error was raised...\n %s' % repr(e))
