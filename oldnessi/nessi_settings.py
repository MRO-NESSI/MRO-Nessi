"""
This file holds all of the names, paths etc. that might change throughout the
life of the instrument.  

Syntax notes:
    The format for each of the items is name = ['item1', 'item2', 'item3']
    it is important that ONLY item1, item2 etc. are changed.  If there is an 
    open space in the wheel, label it as 'open'.  Do not change the number of 
    items in the list.
    
    The port listings are based on locations in Ubuntu, this may vary slightly 
    depending on the linux distro used.
"""

##This sets the label names for the power buttons, 0-7
relay_labels = ['Alta U6:', 'MVBlueFox:', 'Pyxis Rotator:', 'Apogee FW:', 'Laser:', 'Linear Stage:', 'Mask Wheel:', 'Filter Wheel:']

##This sets the names of the choices for the guide camera filter wheel, 0-9
grism = ['Low (R250)', 'J (R1000)', 'H (R1000)', 'K (R1000)', 'Imaging']

##This sets the names of the choices for the main filter wheel, 0-6
fw = ['Open', 'J', 'H', 'K', 'Wideband']

##This sets the names of the choices for the mask wheel, 0-6 
mask = ['Field 1', 'Field 2', 'Field 3', 'Field 4', 'Field 5', 'Field 6', 'Field 7', 'Field 8', 'Open', 'Dark']

##Rotator Step Size
step = 0 # full step = 0, half step = 1

##Global Logging
logging = 0 # 0 = no logging, 1 = logging

##Log Folder - what folder to save log to
logloc = "/tmp/"

##Relay/power control board serial port
relay_port = '/dev/ttyUSB0'

##Temperature probe serial port
temp_port = '/dev/ttyUSB1'

##Pyxis rotator serial port
rot_port = '/dev/ttyUSB2'

##linear focusing stage serial port
focus_port = '/dev/ttyUSB3'
