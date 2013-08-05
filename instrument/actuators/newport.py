#!/usr/bin/env python

from configobj import ConfigObj
import math
import time
import threading
from wx.lib.pubsub import Publisher

import XPS_C8_drivers as xps
from threadtools import run_async
from instrument.component import InstrumentError

cfg = ConfigObj(infile="nessisettings.ini")
fpa_limit_flag = threading.Event()

def XPSErrorHandler(controller, socket, code, name):
    """This is a general error handling function for the newport controller 
    functions. First the function checks for errors in communicating with the 
    controller, then it fetches the error string and displays it in a message 
    box. If the error string can not be found it will print the error code for
    lookup by the user.

        Arguments: controller, socket, code, name.

            controller: [xps]   Which instance of the XPS controller to use.
            socket:     [int]   Which socket to use to communicate with the XPS 
                                controller.
            code:       [int]   The error code returned by the function that 
                                called this function.
            name:       [str]   The name of the function that called this 
                                function.

        Returns: None.

        Raises: InstrumentError.
    """
    errstr = ''
    fatality = None
    
    # This checks to see if the error is in communication with the controller.
    if code != -2 and code != -108:

        fatality = False
        # Getting the error string.
        error = controller.ErrorStringGet(socket, code)
        # If the error string lookup fails, this message will display with 
        # the error code.
        if error[0] != 0:
            errstr = name + " : ERROR "+ str(code)
        # This displays the error string.
        else:
            errstr = name + " : " + error[1]
    # This code handles the case where the connection to the controller fails
    # after initial contact.
    else:
    
        fatality = True
        if code == -2:
            errstr = name + " : TCP timeout"
        elif code == -108:
            errstr = name + " : The TCP/IP connection was closed by an" + \
                            "administrator"
        
    raise InstrumentError(errstr)

def NewportWheelHome(controller, wheel, socket):
    """This function homes a dewar wheel.  This function will call the 
    XPSErrorHandler function if any of the newport commands fail. Information
    about the specific homing of the motors is contained in the nessisettings
    configuration file.  This function does not have a Timeout and can run 
    indefinitely if there are problems with the switches. 
    
        Arguments: controller, socket, wheel.

            controller: [xps]   Which instance of the XPS controller to use.
            socket:     [int]   Which socket to use to communicate with the XPS 
                                controller.
            wheel:      [str]   The name of the function that called this 
                                function.

        Returns: None.

        Raises: InstrumentError.
            
            InstrumentError:    This is raised if the wheel fails to home.
    """
    # Config-file based variables.
    group     = cfg[wheel]["group"]
    speed     = int(cfg[wheel]["direction"])*30
    wheel_gap = int(cfg[wheel]["direction"])*340
    homeval   = int(cfg[wheel]["home"]["val"])
    homebit   = int(cfg[wheel]["home"]["bit"])
    posval    = int(cfg[wheel]["position"]["val"])
    posbit    = int(cfg[wheel]["position"]["bit"])  

    # Start of the algorithm.  If the wheel is not at a position it goes to one. 
    value = controller.GPIODigitalGet(socket, "GPIO4.DI")

    # This part of the if statement checks for an error reading the the GPIO.
    if value[0] != 0:
        XPSErrorHandler(controller, socket, value[0], "GPIODigitalGet")

    # This portion initiates a slow move forward to find the next position if it
    # is not already at one.  If it is then it passes to the next part of the 
    # function.
    elif int(format(value[1], "016b")[::-1][posbit]) != posval:
        Gset = controller.GroupSpinParametersSet(socket, group, speed, 800)
        while True:
            time.sleep(.1)
            value = controller.GPIODigitalGet(socket, "GPIO4.DI") 
            if value[0] != 0:
                XPSErrorHandler(controller, socket, value[0], 
                                "GPIODigitalGet")
            elif int(format(value[1], "016b")[::-1][posbit]) == posval:
                stop=controller.GroupSpinModeStop(socket, group, 1200)
                if stop[0] != 0:
                    XPSErrorHandler(controller, socket, stop[0],
                                    "GroupSpinModeStop")
                break
            else:
                pass
    else:
        pass

    # This section of the function checks to see if the wheel is already homed.
    # If so then the function returns otherwise it begins moving to each 
    # successive position until it finds the home position. 
    value = controller.GPIODigitalGet(socket, "GPIO4.DI")
    if value[0] != 0:
        XPSErrorHandler(controller, socket, value[0], 
                        "GPIODigitalGet")
    elif int(format(value[1], "016b")[::-1][homebit]) == homeval:
        return
    else:
        pass

    # This section controls motion between positions.  First it moves the motor
    # a known distance to be close to the next position, then the motor is moved
    # slowly until the next position is reached.  This is determined by a while
    # loop that reads the position switch to see when it opens.  Once at a 
    # position the home switch is checked to see if the wheel has arrived.  If 
    # so then the function returns, otherwise the loop repeats, moving to the 
    # next position.
    for i in range(8):
        # Moving close to the next position.
        for j in range(2):
            GMove = controller.GroupMoveRelative(socket, group, [wheel_gap])
            if GMove[0] != 0:
                XPSErrorHandler(controller, socket, GMove[0], 
                                "GroupMoveRelative")
        # Starting slow motion to the next position.
        Gset = controller.GroupSpinParametersSet(socket, group, speed, 
                                                 800)
        # Checking if the motion command was sent correctly.
        # If so then the GPIO checking begins.
        if Gset[0] != 0:
            XPSErrorHandler(controller ,socket, Gset[0],
                            "GroupSpinParametersSet")
        else:
            # The while loop checks for a position switch to open.
            while True:
                time.sleep(.1)
                value = controller.GPIODigitalGet(socket, "GPIO4.DI")
                if value[0] != 0:
                    XPSErrorHandler(controller, socket, value[0],
                                    "GPIODigitalGet")
                elif int(format(value[1], "016b")[::-1][posbit]) == posval:
                    stop=controller.GroupSpinModeStop(socket, group, 1200)
                    if stop[0] != 0:
                        XPSErrorHandler(controller, socket, stop[0],
                                        "GroupSpinModeStop")
                    break
                else:
                    pass
        # Once at a position, the home switch is checked to see if it is the 
        # home position.  If so then the function returns, otherwise this 
        # iteration of the loop passes.
        value = controller.GPIODigitalGet(socket, "GPIO4.DI")
        if value[0] != 0:
            XPSErrorHandler(controller, socket, value[0], 
                            "GPIODigitalGet")
        elif int(format(value[1], "016b")[::-1][homebit]) == homeval:
            return
        else:
            pass

    value = controller.GPIODigitalGet(socket, "GPIO4.DI")
    if value[0] != 0:
        XPSErrorHandler(controller, socket, value[0], 
                            "GPIODigitalGet")
    elif int(format(value[1], "016b")[::-1][homebit]) == homeval:
        return
    else:
        message = "Error: Homing of " + str(wheel) + \
                  " failed.  Retry or check switches."
        raise InstrumentError(message)


def NewportWheelMove(controller, wheel, socket, current, position):
    """This function moves a dewar wheel to a selected position.  Since the 
    positions are identical this is done by moving a determined number of 
    positions from the current (known) position.  If the position is not known
    then the wheel should be homed first.  This function does not have a
    Timeout and can run indefinitely if there are problems with the switches.

        Arguments: controller, name, socket, current, position.

            controller: [xps]   Which instance of the XPS controller to use.
            wheel:      [str]   The name of the motor that is being used.  
                                This is for config file purposes.
            socket:     [int]   Which socket to use to communicate with the XPS 
                                controller.
            current:    [int]   What position the motor is currently at.
            position:   [int]   What position the motor should move to.
        
        Returns: position
            
            position:   [int]   Theposition the motor moved to based on switch 
                                counts.
    
        Raises: None
    """
    # Initializing config-file specific variables.
    group     = cfg[wheel]["group"]
    speed     = int(cfg[wheel]["direction"])*30
    wheel_gap = int(cfg[wheel]["direction"])*340
    val       = int(cfg[wheel]["position"]["val"])
    bit       = int(cfg[wheel]["position"]["bit"])
    # diff is how many positions away from current the target position is.
    diff      = (int(cfg[wheel]["slots"]) - current + position) % \
                int(cfg[wheel]["slots"])

    # First there is a check to see if the motor is already at the current 
    # position. This check is only a check of inputs.  It does not check to see
    # if the motor is in a position.  If a motor has been moved by hand or if a
    # previous move had failed then this check could still pass despite being
    # wrong.
    if current != position:
        # If the motor passes the theoretical check then the function checks to 
        # see if the motor is on a switch. If it is not for some reason then it 
        # moves forward slowly until it finds a switch and sets the movement 
        # counter down by one.  This is because it is a known error that the 
        # motor can detect a switch being flipped but not stop in time.
        value = controller.GPIODigitalGet(socket, "GPIO4.DI")
        if value[0] != 0:
            XPSErrorHandler(controller, socket, value[0], "GPIODigitalGet")
        elif int(format(value[1], "016b")[::-1][bit]) != val:
            Gset = controller.GroupSpinParametersSet(socket, group, speed,
                                                     800)
            while True:
                time.sleep(.1)
                value = controller.GPIODigitalGet(socket, "GPIO4.DI")
                if value[0] != 0:
                    XPSErrorHandler(controller, socket, value[0], 
                                    "GPIODigitalGet")
                elif int(format(value[1], "016b")[::-1][bit]) == val:
                    stop=controller.GroupSpinModeStop(socket, group, 1200)
                    if stop[0] != 0:
                        XPSErrorHandler(controller, socket, stop[0],
                                        "GroupSpinModeStop")
                    diff = diff - 1
                    break
                else:
                    pass
        else:
            pass

        # This loop moves the wheel forward one position each iteration and runs
        # until it reaches the specified position.
        for i in range(diff):
            # This loop moves the motor close to the next position quickly.
            for j in range(2):
                GMove = controller.GroupMoveRelative(socket, group, [wheel_gap])
                if GMove[0] != 0:
                    XPSErrorHandler(controller, socket, GMove[0], 
                                    "GroupMoveRelative")
            # Starting slow motion.
            Gset = controller.GroupSpinParametersSet(socket, group, speed,
                                                     800)
            # Checking if the motion command was sent correctly.
            # If so then the GPIO checking begins.
            if Gset[0] != 0:
                XPSErrorHandler(controller ,socket, Gset[0],
                                "GroupSpinParametersSet")
            else:
                # This loop monitors the position switch to stop the motor when 
                # it reaches the switch.
                while True:
                    time.sleep(.1)
                    value = controller.GPIODigitalGet(socket, "GPIO4.DI")
                    if value[0] != 0:
                        XPSErrorHandler(controller, socket, value[0],
                                        "GPIODigitalGet")
                    elif int(format(value[1], "016b")[::-1][bit]) == val:
                        stop=controller.GroupSpinModeStop(socket, group, 1200)
                        if stop[0] != 0:
                            XPSErrorHandler(controller, socket, stop[0],
                                            "GroupSpinModeStop")
                        break
                    else:
                        pass
            
        return position
    
    else:
        return position
                


def NewportInitialize(controller, motor, socket, home_pos):
    """An initialization function for any motor controlled by the XPS 
    controller. This function returns nothing if succesful and calls 
    XPSErrorHandler otherwise.

        Arguments: controller, motor, socket, home_position.
    
            controller: [xps]   Which instance of the XPS controller to use.
            motor:      [str]   The name of the motor that is being used.  This 
                                is for config file purposes.
            socket:     [int]   Which socket to use to communicate with the XPS 
                                controller.
            home_pos:   [int]   What position on the motor is defined as home.

        Returns: None.

        Raises: None.
    """
    # This function kills any motors that are still active from previous 
    # motions.
    GKill = controller.GroupKill(socket, cfg[motor]["group"])   
    if GKill[0] != 0:
        XPSErrorHandler(controller, socket, GKill[0], "GroupKill")

    # This function initializes the motor so it can be moved.
    GInit = controller.GroupInitialize(socket, cfg[motor]["group"])
    if GInit[0] != 0:
        XPSErrorHandler(controller, socket, GInit[0], "GroupInitialize")

    # This function homes the motor and then moves the motor to a home position
    # defined by the user.
    GHomeSearch = controller.GroupHomeSearchAndRelativeMove(socket, 
                                                            cfg[motor]["group"],
                                                            [home_pos])
    if GHomeSearch[0] != 0:
        XPSErrorHandler(controller, socket, GHomeSearch[0], 
                        "GroupHomeSearchAndRelativeMove")


def NewportKmirrorMove(controller, socket, motor, position):
    """This function moves the k-mirror to a choosen position at 10 deg/s.

        Arguments: controller, socket, motor, position.

            controller: [xps]   Which instance of the XPS controller to use.
            socket:     [int]   Which socket to use to communicate with the XPS 
                                controller.
            motor:      [str]   Which motor is being controlled.  This is for 
                                config file purposes.
            position:   [float] What value to move the k-mirror to.

        Returns: None.

        Raises: None.
    """
    # This checks to see if the motor is in a continuous rotation state and if 
    # it is then the function disables continuous rotation. 

    Gmode = controller.GroupJogModeDisable(socket, cfg[motor]["group"])
    if Gmode[0] != 0 and Gmode[0] != -22:
        XPSErrorHandler(controller, socket, Gmode[0], "GroupJogModeEnable")

    # This function sets the motion parameters to be used by the motor.
    # If the parameters are set correctly then an absolute move is made to the 
    # position of choice.
    Gset = controller.PositionerSGammaParametersSet(socket,
                                                    cfg[motor]["positioner"], 
                                                    10 , 200, .005, .05)
    if Gset[0] != 0:
        XPSErrorHandler(controller, socket, Gset[0],
                        "PositionerSGammaParametersSet")
    else:
        GMove = controller.GroupMoveAbsolute(socket, cfg[motor]["group"], 
                                             [float(position)])
        if GMove[0] != 0:
            XPSErrorHandler(controller, socket, GMove[0], "GroupMoveAbsolute")
       
   

def NewportKmirrorRotate(controller, socket, motor, speed):
    """This function prepares the motor for continuous rotation if it isn't 
    already prepared and then sets a choosen velocity.

        Arguments: controller, socket, motor, velocity.

            controller: [xps]   Which instance of the XPS controller to use.
            socket:     [int]   Which socket to use to communicate with the XPS 
                                controller.
            motor:      [str]   Which motor is being controlled.  This is for 
                                config file purposes.
            jog_state:  [bool]  Whether or not the motor in question is already 
                                configured for continuous rotation. 
            velocity:   [float] What value to set the rotational velocity to in 
                                deg/s.
    
        Returns: None.
    
        Raises: None.
    """
    # This checks if the motor is in a continuous rotation state and if not 
    # enables that state.
    Gmode = controller.GroupJogModeEnable(socket, cfg[motor]["group"])
    if Gmode[0] != 0 and Gmode[0] != -22:
        XPSErrorHandler(controller, socket, Gmode[0], "GroupJogModeEnable")
    else:
        pass
    # This sets the rotation rate for the motor. 
    # The motor will rotate until it is stopped or it hits a limit switch.
    velocity = speed*cfg[motor]["direction"]
    GJog = controller.GroupJogParametersSet(socket, cfg[motor]["group"],
                                            [velocity],[400])
    if GJog[0] != 0:
        XPSErrorHandler(controller, socket, GJog[0], "GroupJogParametersSet")

   
def NewportStatusGet(controller, socket, motor):
    """This function retrieves a list of information about the motor. The 
    position of the motor is only accurate for the kmirror.

        Arguments: controller, socket, motor.
    
            controller: [xps]   Which instance of the XPS controller to use.
            socket:     [int]   Which socket to use to communicate with the XPS
                                controller.
            motor:      [str]   Which Motor is being controlled.  This is for 
                                config file purposes.

        Returns: info.
    
            info:       [list]  A list of information about the motor.
                                [position, velocity, acceleration, min jerk
                                time, max jerk time]

        Raises: None.
    """
    # Initializing the empty list.
    info = []
    # Retrieving the position of the motor.
    position = controller.GroupPositionCurrentGet(socket, cfg[motor]["group"], 
                                                  1)
    if position[0] != 0:
        XPSErrorHandler(controller, socket, position[0],
                        "GroupPositionCurrentGet")
    else:
        info.append(position[1])
    # Getting the rest of the information.
    profile = controller.PositionerSGammaParametersGet(socket, 
                                                       cfg[motor]["positioner"])
    if profile[0] != 0:
        XPSErrorHandler(controller, socket, profile[0],
                        "PositionerSGammaParametersGet")
    else:
        # compiling the list of information.
        for i in profile[1:]:
            info.append(i)
    return info


def NewportStop(controller, socket, motor):
    """This function stops the motion of a given motor.  If the motor in 
    question is the kmirror motor then it also disables its continuous rotation 
    mode.

        Arguments: controller, socket, motor.
    
            controller: [xps]   Which instance of the XPS controller to use.
            socket:     [int]   Which socket to use to communicate with the XPS
                                controller.
            motor:      [str]   Which Motor is being controlled.  This is for 
                                config file purposes.

        Returns: None.

        Raises: None.
    """
    # Checking if the motor is the kmirror motor. If so then it stops the motor
    # and disables jogging. 
    if motor == "kmirror":
        # Stopping.
        GStop = controller.GroupJogParametersSet(socket, cfg[motor]["group"], 
                                                 [0],[200])
        if GStop[0] != 0:
            XPSErrorHandler(controller, socket, GStop[0], 
                            "GroupJogParametersSet")
        else: 
            pass 
        # Disabling jogging.
        JDisable = controller.GroupJogModeDisable(socket, cfg[motor]["group"])
        if JDisable[0] != 0:
            XPSErrorHandler(controller, socket, JDisable[0],
                            "GroupJogModeDisable")
        else: 
            pass   
    # The case for the other motors.  Only a stop command is required.     
    else:
        # Stopping.
        GStop = controller.GroupSpinParametersSet(socket, cfg[motor]["group"],
                                                  0, 800)
        if GStop[0] != 0:
            XPSErrorHandler(controller, socket, GStop[0], 
                            "GroupSpinParametersSet")
        else:
            pass

@run_async
def NewportFocusLimit(controller, socket, motor):
    """This function is an asynchronus function that monitors the switches for 
    the FPA.  If the FPA reaches one of its limits then the motor is stopped 
    immediately.  If a polite stop fails then a kill all command is sent. 
    
        Arguments: controller, socket, motor.
    
            controller: [xps]   Which instance of the XPS controller to use.
            socket:     [int]   Which socket to use to communicate with the XPS
                                controller.
            motor:      [str]   Which Motor is being controlled.  This is for 
                                config file purposes.
    
        Returns: None.

        Raises: None.

    """
    # Setting config-file variables.
    bitup = cfg[motor]["upper"]["bit"]
    bitdown = cfg[motor]["lower"]["bit"]
    valup = cfg[motor]["upper"]["val"]
    valdown = cfg[motor]["lower"]["val"]
    stop = False
    limit = False

    # This while loop runs until the motor is stopped by a different function or
    # it runs into a limit switch. 
    while stop == False:
        # Polling the controller for motor info.
        value = controller.GPIODigitalGet(socket, "GPIO4.DI")
        velocity = controller.GroupVelocityCurrentGet(socket, 
                                                      cfg[motor]["group"])
        
        # If either of the polls fails then the loop and the motor are stopped.
        if value[0] != 0 or velocity[0] != 0:
            fpa_limit_flag.clear()
            limit = True
            stop = True
            if value[0] != 0:
                XPSErrorHandler(controller, socket, value[0], "GPIODigitalGet")
            else:
                XPSErrorHandler(controller, socket, velocity[0], 
                                "GroupVelocityCurrentGet")

        # Checking if either of the switches are reached.
        elif int(format(value[1], "016b")[::-1][bitup]) == valup or \
             int(format(value[1], "016b")[::-1][bitdown]) == valdown:
            fpa_limit_flag.clear()
            limit = True
            stop = True

        # Checking if the motor was stopped.
        elif fpa_limit_flag.is_set() == False:
            stop = True

        else:
            pass 

    if limit == True:
        # Stopping the motor politely.
        kill = controller.GroupKill(socket, cfg[motor]['group'])
        if kill[0] != 0:
            # Stopping the motor impolitely.
            killall = controller.KillAll(socket)
            if killall[0] != 0:
                XPSErrorHandler(controller, socket, killall[0], "KillAll")
            XPSErrorHandler(controller, socket, kill[0], "GroupKill")
           

def NewportFocusMove(controller, socket, motor, distance, speed, direction):
    """This function moves the FPA.  The user sets the distance speed and 
    direction of the motion.  
        Arguments: controller, socket, motor, distance, speed, direction.

            controller: [xps]   Which instance of the XPS controller to use.
            socket:     [list]  A list of two sockets to use to communicate with 
                                the XPS controller.
            motor:      [str]   Which motor is being controlled.  This is for 
                                config file purposes.
            distance:   [float] How far to move the array (in micrometers).
            speed:      [int]   How fast to move the array.
            direction:  [+-1]   which direction to move.
    
        Returns: travel.

            travel:     [float] How far the motor moved in micrometers.  In the 
                                case of an error this will be set to the string 
                                'ERROR'.
    
        Raises: None.
"""
    # Initializing variables of motion and setting the fpa_limit_flag to true.
    fpa_limit_flag.set()
    deg_distance = distance*.576
    velocity = speed 
    true_direction = direction * cfg[wheel]['direction']
    # initializing the motors motion profile and checking to for success.
    SGamma = controller.PositionerSGammaParametersSet(socket[1], 
                                                      cfg[wheel]["positioner"], 
                                                      velocity, 600, .005, .05)
    if SGamma[0] != 0:
        fpa_limit_flag.clear()
        XPSErrorHandler(controller, socket[1], SGamma[0], 
                        "PositionerSGammaParametersSet")                
    
    # determining how many rotaions to move the motor.
    count = int(math.floor(deg_distance/360))
    remainder = true_direction * (deg_distance % 360)

    # Starting the monitoring thread.
    NewportFocusLimit(controller, socket[0], motor)
    
    # This loop checks to be sure the motor is allowed to move.  If so then it 
    # rotates the motor 360 degrees in the appropriate direction and then 
    # repeats.
    for i in range(count):
        # Check of motor movability.
        if fpa_limit_flag.is_set() == False:
            return 'ERROR'
        
        else:
            # Movement.
            GMove = controller.GroupMoveRelative(socket[1], cfg[motor]["group"], 
                                             [true_direction * 360])
            if GMove[0] != 0:
                XPSErrorHandler(controller, socket[1], Gmove[0], 
                                "GroupMoveRelative")
    # A last check to determine if the motor can move.
    if fpa_limit_flag.is_set() == False:
        return 'ERROR'
    
    # Moving the motor the last fraction of a rotation.
    else:
        GMove = controller.GroupMoveRelative(socket[1], cfg[motor]["group"], 
                                             [remainder])
        if GMove[0] != 0:
            XPSErrorHandler(controller, socket[1], Gmove[0], 
                            "GroupMoveRelative")

    # Returning the distance traveled and setting the fpa_limit_flag to false so
    # that the limit tracking thread stops.
    travel = distance   
    fpa_limit_flag.clear()
    return travel 
    

def NewportFocusHome(controller, socket, motor):
    """This function homes the FPA .  It runs the FPA towards the bottom of its
    motion until it hits the lower limit switch.  When it reaches the switch a 
    stop command is sent.  If that fails then kill commands will be sent.

        Arguments: controller, socket, motor.
    
            controller: [xps]   Which instance of the XPS controller to use.
            socket:     [int]   Which socket to use to connect to the XPS 
                                controller.
            motor:      [str]    Which motor is being controlled.  This is for 
                                config file purposes. 

        Returns: None.

        Raises: None.
    """
    # Initializing motor variables.
    bitdown = cfg[motor]["lower"]["bit"]
    valdown = cfg[motor]["lower"]["val"]
    vel = -200*cfg[wheel]['direction']
    group = cfg[wheel]['group']
    
    # Starting motion. 
    Gset = controller.GroupSpinParametersSet(socket, cfg[wheel]["group"], 
                                             vel, 200)
    if Gset[0] != 0:
        XPSErrorHandler(controller ,socket, Gset[0], "GroupSpinParametersSet")
    else:
        # This loop watches for the limit switch to be activated.
        while True:
            value = controller.GPIODigitalGet(socket, "GPIO4.DI")
            if int(format(value[1], "016b")[::-1][bitdown]) == valdown:
                break
            else:
                time.sleep(.1)
    # When the loop terminates a stop command is sent.  If that command fails a
    # group kill command is sent.  If that fails a kill all command is sent. 
    stop = controller.GroupSpinModeStop(socket, group, 400)
    if stop[0] != 0:
        Kill = controller.GroupKill(socket, group)
        if Kill[0] != 0:
            KillAll = controller.KillAll(socket)
            if KillAll[0] != 0:
                XPSErrorHandler(controller, socket, KillAll[0], "KillAll")            
            XPSErrorHandler(controller, socket, Kill[0], "GroupKill")        
        XPSErrorHandler(controller, socket, stop[0], "GroupSpinModeStop")    
    else:
        pass


def NewportKmirrorTracking(parent, controller, socket, motor, t_angle):
    """
This function initiates kmirror tracking.  The tracking algorith updates the
speed of rotation based on feedback from the telescope.  If the telescope is 
not returning data then the tracking is cancelled.  tracking runs until the 
user stops it in the NESSI GUI.
    
    Inputs: parent, controller, socket, motor.
    
    parent:     [???]   The object that called the function.
    controller: [xps]   Which instance of the XPS controller to use.
    socket:     [int]   Which socket to be used to communicate with the XPS
                        controller.
    motor:      [str]   Which motor is being used.  This is for config file
                        purposes.
    t_angle:    [float] User defined angle specific to the target.

"""
    Gmode = controller.GroupJogModeEnable(socket, cfg[motor]["group"])
    if Gmode[0] != 0:
        XPSErrorHandler(controller, socket, Gmode[0], "GroupJogModeEnable")
    phi = math.radians(33.984861)
    
    while parent.trackstatus == True:
        try:
            A = math.radians(parent.keywords['TELAZ'])
            H = math.radians(parent.keywords['TELALT'])
            PA = float(parent.keywords['PA'])
        except TypeError:
            parent.trackstatus = False
            time.sleep(1)
        else:
            angle = .5*(t_angle - PA - cfg['motor']["direction"]*H)
            vel = ((-.262)*(.5)*3600*math.pi*math.cos(phi)*math.cos(A))/\
                  (math.cos(H)*180)
            delta = vel - parent.vel
            parent.vel = parent.vel + delta
            velocity = parent.vel*cfg[motor]["direction"]
            GJog = controller.GroupJogParametersSet(socket, cfg[motor]["group"],
                                                    [velocity],[400])
            if GJog[0] != 0:
                XPSErrorHandler(controller, socket, GJog[0],
                                "GroupJogParametersSet")
            position = controller.GroupPositionCurrentGet(socket, 
                                                          cfg[motor]["group"],
                                                          1)
            if position[0] != 0:
                XPSErrorHandler(controller, socket, position[0],
                                "GroupPositionCurrentGet")
            diff_angle = position[1] - angle           
            time.sleep(1)
        

def NewportKill(controller, motor, socket):
    try:
        kill = controller.GroupKill(socket, cfg[motor]['group'])
        if kill[0] != 0:
            XPSErrorHandler(controller, socket, kill[0], "GroupKill")
    
    except:
        killall = controller.KillAll(socket)
        if killall[0] != 0:
            XPSErrorHandler(controller, socket, killall[0], "KillAll")

# Test code to be removed later
if __name__ == "__main__":

    x=xps.XPS()
    open_sockets=[]
    used_sockets=[]

    for i in range(int(cfg["general"]["sockets"])):
        open_sockets.append(x.TCP_ConnectToServer("192.168.0.254",5001,1))
    
    for i in range(int(cfg["general"]["sockets"])):
        if open_sockets[i] == -1:
            print "Error, Sockets not opened."
    NewportInitialize(x, "mask", open_sockets[0], 0)
    pos = NewportWheelThread(x, "mask", open_sockets[0], 1, 4, True)
    pos = NewportWheelThread(x, "mask", open_sockets[0], pos, 1, False)

    
