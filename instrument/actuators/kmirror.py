from threadtools import run_async
import math
import instrument.actuators.newport as np
from instrument.component import InstrumentComponent, InstrumentError, logCall


class KMirror(InstrumentComponent):
    """Represents the Newport controlled K-Mirror.

    Methods:
        initialize
        kill
        move
        stop
        track
    """

    def __init__(self, instrument, controller, sockets):
        """Connects to, initializes, and homes a specified wheel in the dewar. 

        Arguments:
            instrument -- Copy of the NESSI instrument
            controller -- XPS instance to use for control 
            sockets    -- List of integers representing TCP sockets

        Raises:
             InstrumentError
        
        Returns:
            None
        """

        super(KMirror, self).__init__(instrument)
        
        self.motor = 'kmirror'
        self.controller = controller
        self.sockets = sockets
        self.home_pos = 0
        self.current_pos = 0
        self.track_status = False

        self.initialize()

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

        except InstrumentError as e:
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

        except InstrumentError as e:
            raise InstrumentError('An error occured during a kill sequence of'
                                  ' the K-Mirror.\n The following '
                                  ' error was raised...\n %s' % repr(e))

    @property
    def positionAngle(self):
        return np.NewportStatusGet(self.controller, self.sockets[1], 
                                   self.motor)[0]

    def userAngleToPositionAngle(self, userAngle):
        if self.instrument.telescope:
            parallactic_angle = self.instrument.telescope.parallactic_angle
            altitude      = self.instrument.telescope.altitude
            tmode         = int(self.instrument.cfg['kmirror']['direction'])
            positionAngle = 0.5 * ((userAngle - parallactic_angle) 
                                 - tmode * (altitude))
            return positionAngle
        else:
            return None
        
        

    @logCall(msg='Moving KMirror.')
    def move(self, position):
        """Moves the wheel to a selected position.
            
        Arguments:
            position -- Which position [float] to move to. Limited to +-170.

        Raises:
            InstrumentError
        
        Returns:
            None
        """
        try:
            with self.lock:
                np.NewportKmirrorMove(self.controller, self.sockets[0], 
                                   self.motor, position)
                self.current_pos = self.positionAngle

        except InstrumentError as e:
            raise InstrumentError('An error occured during a movement of'
                                  ' the K-Mirror. \n The following '
                                  ' error was raised...\n %s' % repr(e))

    def moveToUserAngle(self, userAngle):
        pa = self.userAngleToPositionAngle(userAngle)
        if not pa:
            raise InstrumentError('Unable to produce Position Angle from'
                                  'user angle!')
        self.move(self.userAngleToPositionAngle(userAngle))


    def setVelocity(self):
        vel = self.calculateVelocity()
        if not vel:
            raise InstrumentError('Unable to produce new velocity for'
                                  'tracking.')
        self.updateVelocity(self.calculateVelocity())
        

    def calculateVelocity():
        if self.instrument.telescope:
            phi = math.radians(33.984861)
            azimuth   = self.instrument.telescope.azimuth
            altitude  = self.instrument.telescope.altitude
            vel       = ((-.262)*(.5)*180*math.cos(phi)*math.cos(azimuth))/\
                        (math.cos(altitude)*3600*math.pi)
            return vel
        else:
            return None
        
    

    @logCall(msg='Stepping KMirror.')   
    def step(self, offset):
        """Moves by a given offset angle.
        
        Arguments:
            offset -- Angle offset to move.

        Raises:
            Instrument Error
        
        Returns:
            None
        """
        self.move(offset + self.positionAngle)

    @logCall(msg='Homeing the Kmirror.')
    def home(self):
        """Moves motor to position 0.

        Arguments:

        Raises:
            InstrumentError 

        Returns:
            None
        """
        self.move(0)

    @logCall(msg='Stopping KMirror.')
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
            np.NewportStop(self.controller, self.sockets[2], self.motor)
        
        except InstrumentError as e:
            raise InstrumentError('An error occured during a stop sequence of'
                                  ' the K-Mirror.\n The following '
                                  ' error was raised...\n %s' % repr(e))    
    @logCall(msg='Tracking KMirror')
    @run_async(daemon=True)
    def track(self, t_angle, track_event):
        """Starts the K-Mirror tracking loop.
            
        Arguments:
            t_angle -- A user defined value specific to the tracking target.
            track_event --- threading.Event object to signal when tracking
                            is finished.

        Raises:
            InstrumentError
        
        Returns:
            None
        """
        try:
            np.NewportKmirrorTracking(self, self.controller, self.sockets[0],
                                      self.motor, t_angle, track_event)        
        except InstrumentError as e:
            raise InstrumentError('An error occured during a stop sequence of'
                                  ' the K-Mirror.\n The following '
                                  ' error was raised...\n %s' % repr(e))
    @logCall(msg='Updating KMirror velocity.')
    def updateVelocity(self, vel):
        """Moves the KMirror at a set velocity.
            
        Arguments:
            vel -- Which velocity [float] to set the kmirror motor to.

        Raises:
            InstrumentError
        
        Returns:
            None
        """
        try:
            with self.lock:
                np.NewportKmirrorRotate(self.controller, self.sockets[0], 
                                   self.motor, vel)
        except InstrumentError as e:
            raise InstrumentError('An error occured during a velocity set of'
                                  ' the K-Mirror. \n The following '
                                  ' error was raised...\n %s' % repr(e))


