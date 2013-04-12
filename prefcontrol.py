import configobj
import os
import sys
 
appPath = os.path.abspath(os.path.dirname(os.path.join(sys.argv[0])))
inifile = os.path.join(appPath, "example.ini")
 
########################################################################
def createConfig():
    """
    Create the configuration file
    """
    config = configobj.ConfigObj()
    config.filename = inifile
    config['scope server'] = "192.168.0.2"    
    config['scope port'] = 7624
    config['savefolder'] = "/home/lschmidt/Downloads/"
    config['instrument port'] = -1
    config['pixel scale x'] = 6.472222222222E-05
    config['pixel scale y'] = 6.472222222222E-05
    config['Observer'] = "Observer"
    config.write()
 
#----------------------------------------------------------------------
def getConfig():
    """
    Open the config file and return a configobj
    """
    if not os.path.exists(inifile):
        createConfig()
    return configobj.ConfigObj(inifile)