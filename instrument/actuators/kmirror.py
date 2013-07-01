import newport as np
from instrument.component import InstrumentComponent, InstrumentError

class KMirror(InstrumentComponent):
    """Represents the Newport controlled K-Mirror.

    Methods:
        initialize
        kill
        move
        stop
        track
    """

    def __init__(self, instrument, motor, controller, sockets):
        """Connects to, initializes, and homes a specified wheel in the dewar. 

        Arguments:
            instrument -- Copy of the NESSI instrument
            motor      -- Name of the motor to control [str] 
            controller -- XPS instance to use for control 
            sockets    -- List of integers representing TCP sockets

        Raises:
             InstrumentError
        
        Returns:
            None
        """

        super(KMirror, self).__init__(instrument)
        
        self.motor = motor
        self.controller = controller
        self.sockets = sockets
        self.home_pos = 0
        self.current_pos = 0
        self.track_status = False

        self.initialize()
        self.home()

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
                self.track_status = False
                np.NewportInitialize(self.controller, self.motor,
                                     self.sockets[0], self.home_pos)
                self.current_pos = 0

        except Exception as e:
            raise InstrumentError('An error occured during initialization of'
                                  ' the K-Mirror.\n The following '
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
            self.track_status = False
            np.NewportKill(self.controller, self.motor, self.sockets[1])

        except Exception as e:
            raise InstrumentError('An error occured during a kill sequence of'
                                  ' the K-Mirror.\n The following '
                                  ' error was raised...\n %s' % repr(e))

    def move(self, position):
        """Moves the wheel to a selected position.
            
        Arguments:
            position -- Which position [float] to move to. Limited to +-170.

        Raises:
            InstrumentError
        
        Returns:
            self.current_pos -- The current [float] position of the wheel. 
        """
        try:
            with self.lock:
                np.NewportKmirrorMove(self.controller, self.socket[0], 
                                   self.motor, position)
                self.current_pos = NewportStatusGet(self.controller, 
                                                    self.socket[0], motor)[0]

        except Exception as e:
            raise InstrumentError('An error occured during a movement of'
                                  ' the K-Mirror. \n The following '
                                  ' error was raised...\n %s' % repr(e))

    def stop(self):
        """Stops motion politely. Called to stop tracking.
            
        Arguments:
            None

        Raises:
            InstrumentError
        
        Returns:
            None
        """
        try:
            self.track_status = False
            np.NewportStop(self.controller, self.socket[2], self.motor)
        
        except Exception as e:
            raise InstrumentError('An error occured during a stop sequence of'
                                  ' the K-Mirror.\n The following '
                                  ' error was raised...\n %s' % repr(e))    

    def track(self, t_angle):
        """Starts the K-Mirror tracking loop.
            
        Arguments:
            t_angle -- A user defined value specific to the tracking target.

        Raises:
            InstrumentError
        
        Returns:
            None
        """
        try:
            self.track_status = True
            np.NewportKmirrorTracking(self, self.controller, self.socket[0],
                                      self.motor, t_angle)
        
        except Exception as e:
            raise InstrumentError('An error occured during a stop sequence of'
                                  ' the K-Mirror.\n The following '
                                  ' error was raised...\n %s' % repr(e))
