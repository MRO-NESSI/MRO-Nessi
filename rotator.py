"""API to talk to the Kmirror rotator.  

The rotator command definitions can be found in the Pyxis Technical Manual.

Usage:
    k = Kmirror() # Optionally providing the port as an argument.

    # Getting pointing information
    degrees = k.get_pa()
    radians = k.get_pa_rad()

    # Moving the rotator
    k.set_pa(degrees)
    k.set_pa_rad(radians)

    # If the rotator loses its bearing for some reason:
    k.reset()
"""
import math
import serial
import threading
import subprocess
import time

# Set the system path to the root directory of the Nessi set of libraries so we 
# can import our library modules in a consistent manner.
# uncomment lines below for stand alone testing.
# import os, sys
# sys.path[0] = os.path.split(os.path.abspath(sys.path[0]))[0]


import gui.amasing_settings as settings

DEBUG = True
count = 0
CW  = 0 # ClockWise rotation direction
CCW = 1 # CounterClockWise rotation direction
full = 0 # Step size is full 
half = 1 # Step size is 1/2

class KmirrorSettings:
    """Basic functions of the rotator, resetting, changing defaults etc."""
    
    def __init__(self, port=settings.rot_port):
        """Performs necessary startup procedures."""
        self.__port = port

        # Establish a connection to the Pyxis rotator
        self.ser = serial.Serial(port=self.__port, baudrate=19200, bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                                 timeout=1)

    def __del__(self):
        """Perform cleanup operations."""
        self.ser.close()

    def get_tracking_dir(self):
        """Read the direction flag from the rotator and return Kmirror.CW or Kmirror.CCW"""
        self.ser.write("CMREAD")
        if DEBUG: print "DEBUG: CMREAD"

        ret = int(self.ser.read(3))
        # Sorry for this sketchiness; python doesn't have a ternary operator.
        if DEBUG: print "DEBUG: %s" % ((ret == Kmirror.CW) and ["CW"] or ["CCW"])[0]
        return ret

    def set_tracking_dir(self, td):
        """Set the direction flag on the rotator to Kmirror.CW or Kmirror.CCW"""
        if td != Kmirror.CW and td != Kmirror.CCW:
            raise ValueError("The tracking direction must be Kmirror.CW or Kmirror.CCW")

        self.ser.write("CD%1dxxx" % td)
        if DEBUG: print "DEBUG: CD%1dxxx" % td

    def set_rate(self, rt):
        """Set the tracking rate via step delay from 00 to 99ms, default is 08ms"""
        if DEBUG: print "CTxx%02d" % rt
        self.ser.write("CTxx%02d" % rt)
        count = 0
        while True:
            ch = self.ser.read()
            if DEBUG: print ch
            if ch == '\n': # Catching old newline
                continue
            if ch == '!': # ok
                if DEBUG: print "rate is set to " + str(rt)
                break
            else:
                raise RuntimeError("Step delay could not be set.")        
        
    def set_stepsz(self, sz):
        """Set the step size flag on rotator to Kmirror.full or Kmirror.half"""
        if sz != Kmirror.full and sz != Kmirror.half:
            raise ValueError("The step size must be either Kmirror.full or Kmirror.half")
            
        self.ser.write("CZ%1dxxx" % sz)

class KmirrorStart(threading.Thread):
    """Group of functions to initialize rotator and make sure we start from zero"""
    def __init__(self, window, port=settings.rot_port, home=False):
        super(KmirrorStart, self).__init__()

        """Performs necessary startup procedures."""
        self.__port = port
        self.__home = home
        self.window = window
    
    def step_to_angle(self, step):
        """Input current step count, get angle"""
        step_per_rot = 46080
        arcmin_per_step = 0.46875
        
        #get current angle
        current = count
        angle = current*arcmin_per_step/60
        return angle    
       
    def run(self):
        """Force the K-mirror to find its home position.  Raises RuntimeError if
        this cannot be done because human intervention will be required.
        """
        self.ser = serial.Serial(port=self.__port, baudrate=19200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
                
        self.ser.write("CCLINK")
        time.sleep(0.1)
        ready = self.ser.read(self.ser.inWaiting())
                    
        if DEBUG: print 'rot ready=', ready
        if '!' in ready:
            self.ser.write("CTxx02")
            time.sleep(0.02)
            rate = self.ser.read(self.ser.inWaiting())
            if '!' in rate:
                if DEBUG: print "Rate set to 02"
                
            if DEBUG: print "Rotator Ready"
            pass
        else:
            self.__home = True
            
        if self.__home:
            self.ser.write("CHOMES")
            if DEBUG: print "DEBUG: CHOMES"

            counter = 0
            while True:
                time.sleep(0.02)
                ch = self.ser.read(self.ser.inWaiting())
 #               if DEBUG: print "ch=", ch
                if '\n' in ch: # Catching old newline
                    continue
                if '!' in ch: # Stepping
                    counter += ch.count('!')
 #                   if DEBUG: print "counter is:", counter
                    if 'F' in ch: # Finished
                        count = 0
                        if DEBUG: print "Count set to 0, initialization finished"
                        self.ser.close()
                        break
                    continue
                if 'F' in ch: # Finished
                    count = 0
                    if DEBUG: print "Count set to 0, initialization finished"
                    self.ser.close()
                    break
                if '1' in ch: # Magnet cannot be found
                    raise RuntimeError("Rotator is jammed.")
            if DEBUG: print "DEBUG: Moved by %d steps." % counter

        ua = self.step_to_angle(count)
        self.window.AfterStart(ua)
        

class MoveThread(threading.Thread):
    """Move the rotator and keep track of its position angle, used to make large 
    moves to a new static angle."""
    def __init__(self, window, user_angle=0.0, tmode=0, track=0, tport=settings.tport, port=settings.rot_port):
        super(MoveThread, self).__init__()
        
        # Attributes
        # tracking mode
        """Position Angle (1)  - maintain fixed angle relative to North
           Vertical Angle (-1) - maintain fixed angle relative to elevation axis - Not Currently Implimented
           stationary mode (0) - mantain fixed rotator angle, no tracking """
        
        self.window = window
        self.__angle = user_angle
        # Which rotator tracking mode is used
        self.__tmode = tmode
        # Enable Tracking
        self.__track = track
        # which port the instrument is mounted to
        self.__tport = tport
        # serial port of rotator
        self.__port  = port
        self.moving = False
                
        # Establish a connection to the Pyxis rotator
        self.ser = serial.Serial(port=self.__port, baudrate=19200, bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                                 timeout=1)
    
    def angle_to_step(self, angle):
        """Input angle in decimal degrees to get number and direction of steps"""
        step_per_rot = 46080
        arcmin_per_step = 0.46875
        
        #get current angle
        current = count
        desired = angle*60/arcmin_per_step
        #calc number of steps and direction  to move to new angle
        if desired == current:
            pass
        elif desired < current:
            dir = 1
            steps = current - desired
            return steps, dir
        elif desired > current:
            dir = 0
            steps = desired - current
            return steps, dir
        
    def step_to_angle(self, step):
        """Input current step count, get angle"""
        step_per_rot = 46080
        arcmin_per_step = 0.46875
        
        #get current angle
        current = count
        angle = current*arcmin_per_step/60
        return angle    
        
    def __move__(self):
        """Move to the desired step location."""
        # 
        self.moving = True
        counter = 0
        global count
        ch = ''
        #find how many moves
        moves = int(self.to_move)
        #find single step moves after 9 step moves
        moves1 = moves%9
        #find number of 9 step moves
        moves9 = (moves-moves1)/9
#        if DEBUG: print 'moves:', moves, 'moves9:', moves9, 'moves1', moves1 
        
        # Direction 0
        if self.dir == 0:
            if DEBUG: print "rotate 0"
            while True:
                if moves-counter < 9:
                    break
                self.ser.write("CXxx09")
                time.sleep(0.02)
                ch = self.ser.read(self.ser.inWaiting())
#                if DEBUG: print ch
                if '\n' in ch: # Catching old newline
                    continue
                if '!' in ch: #stepping
                    counter += ch.count('!')
#                    if DEBUG: print counter
                if counter > moves-9:
#                    if DEBUG: print "9 step moves finished"
                    break
                    
            while True:
                if moves-counter < 1:
                    break
                self.ser.write("CXxx01")
                time.sleep(0.02)
                ch = self.ser.read(self.ser.inWaiting())
#                if DEBUG: print ch
                if '\n' in ch: # Catching old newline
                    continue
                if '!' in ch: #stepping
                    counter += ch.count('!')
#                    if DEBUG: print 'count1:', counter
                if counter == moves:
                    count = count + counter
#                    if DEBUG: print "1 step moves finished"
                    break
                
        #  Direction 1
        if self.dir == 1:
#            if DEBUG: print "rotate 1"
            while True:
                if moves-counter < 9:
                    break
                self.ser.write("CXxx19")
                time.sleep(0.02)
                ch = self.ser.read(self.ser.inWaiting())
#                if DEBUG: print ch
                if '\n' in ch: # Catching old newline
                    continue
                if '!' in ch: #stepping
                    counter += ch.count('!')
#                    if DEBUG: print counter
                if counter > moves-9:
#                   if DEBUG: print "9 step moves finished"
                   break
                    
            while True:
                if moves-counter < 1:
                    break
                self.ser.write("CXxx11")
                time.sleep(0.02)
                ch = self.ser.read(self.ser.inWaiting())
#                if DEBUG: print ch
                if '\n' in ch: # Catching old newline
                    continue
                if '!' in ch: #stepping
                    counter += ch.count('!')
#                    if DEBUG: print counter
                if counter == moves:
                    count = count - counter
#                    if DEBUG: print "1 step moves finished"
                    break

        ua = self.step_to_angle(count)
        if self.__track:
            self.window.thread_status(ua)
        elif not self.__track:
            self.window.after_move(ua)
        self.moving = False
                
    def run(self):
        if DEBUG: print "Moving Rotator..."
        # set to default move delay (4ms) so that it doesn't take too long to move
        self.ser.write("CTxx04")
        if self.__track:
            # Stationary Mode
            if self.__tmode == 0: 
                self.window.thread_status(self.window.ROTPDEST)
                self.window.track_button.Enable()
                
            # Position Angle Mode
            elif self.__tmode == 1:
                while self.window.trackstatus:
                    # Parallactic angle -E, +W
                    self.pa = self.window.keys["pa"]
                    
                    self.el = self.window.keys["telalt"]
                    if DEBUG: print 'pa: ', self.pa, ' el: ', self.el
                    
                    # find desired position angle
                    self.newpa = 0.5*(float(self.__angle) - float(self.pa) - self.__tmode*float(self.el))
                    if DEBUG: print 'newpa: ', self.newpa
                    
                    # move to desired position angle
                    self.to_move, self.dir = self.angle_to_step(self.newpa) 
                    print "to move:", self.to_move, " dir: ", self.dir
                    self.__move__()
                    
                    #continue to sleep if moving
                    while self.moving:
                        time.sleep(0.1)
                        print "sleep a bit"

                    # sleep for a second before next update
                    print "sleep before update"
                    time.sleep(1.0)
                
            # Vertical Angle Mode - Not Implimented
            elif self.__tmode == -1:
                self.window.thread_status(self.window.ROTPDEST)
                self.window.track_button.Enable()

        elif not self.__track:   
            self.to_move, self.dir = self.angle_to_step(self.__angle+self.window.ROTPDEST-self.window.old_ua/2.0) 
            self.__move__()
            if DEBUG: print "Finished Moving Rotator..."
    
#class TrackThread(threading.Thread):
#    """Adjust rotator angle to account for image rotation when tracking on the sky."""
#    def __init__(self, window, user_angle=0.0, tmode=0, port=settings.rot_port):
#        super(TrackThread, self).__init__()
        
#        # Attributes
        
        
#        self.__port  = port
#        # desired angle of rotator relative to North
#        self.__user_angle = user_angle
#        # tracking mode
#        """Position Angle (1)  - maintain fixed angle relative to North
#           Vertical Angle (-1) - maintain fixed angle relative to elevation axis - Not Currently Implimented
#           stationary mode (0) - mantain fixed rotator angle, no tracking """
#        # left (-1) or right (+1) Nasmyth or other (0)
#        self.__tmode = tmode
#        self.window = window

#        # Establish a connection to the Pyxis rotator
#        self.ser = serial.Serial(port=self.__port, baudrate=19200, bytesize=serial.EIGHTBITS,
#                                 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
#                                 timeout=1)
       
#    def __track__(self):
#        # Stationary Mode
#        if self.__tmode == 0: 
#            self.window.thread_status("K-Mirror tracking not necessary for stationary mode.")
#            self.window.track_button.Enable()
            
#        # Position Angle Mode
#        elif self.__tmode == 1:
#            while self.window.trackstatus:
#                if self.window.movestatus:
#                    time.sleep(0.1)
#                else:
#                    self.window.update_keys()
#                    while not self.window.parent.TelescopePanel.done:
#                        time.sleep(0.1)
#                        print self.window.parent.TelescopePanel.done
                        
#                    print self.window.parent.TelescopePanel.done
#                    keys = self.window.keys    
#                    # Parallactic angle -E, +W
#                    self.pa = keys["pa"]
                    
#                    self.el = keys["telalt"]
#                    if DEBUG: print 'pa: ', self.pa, ' el: ', self.el
                    
#                    # find desired position angle
#                    self.newpa = float(self.__user_angle) - float(self.pa) - self.__tmode*float(self.el)
#                    if DEBUG: print 'newpa: ', self.newpa
                    
#                    # move to desired position angle
#                    self.move = MoveThread(self, angle=self.newpa)
#                    #self.move.daemon = True
#                    self.move.start()
#                    self.move.join()
                    
#                    # sleep for a second before next update
#                    time.sleep(1.0)
                
#        # Vertical Angle Mode - Not Implimented
#        elif self.__tmode == -1:
#            self.window.thread_status("K-Mirror tracking mode not implemented.")
#            self.window.track_button.Enable()

##        count = 0 
##        while self.window.trackstatus:
##            count += 1
##            print count
##            time.sleep(1) 

#    def run(self):
#        if DEBUG: print "Rotator Tracking..."
#        # set to default move delay (4ms) so that it doesn't take too long to move
#        self.ser.write("CTxx04")
#        self.__track__()
#        if DEBUG: print "Rotator Tracking Stopped..."