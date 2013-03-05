#!/usr/bin/env python

import usb
# To get this module you will need to download it and install it yourself.  The correct version is not in the package manager.  The package is pyUSB 1.0 


#To find the usb devices I use the command 'lsusb' in the terminal to list the devices. This will list the bus number, device number, IDs, and manufacturer of all devices including internal devices. 

# The controllers are the Future Technology Devices International, Ltd devices. Via the last command I determined that the Vendor ID is 0x0403 and the Product ID is 0xFAF0. This populates the varible 'controllers' with all of the motor controllers present.
controllers = usb.core.find(find_all=True,idVendor=0x0403)

# This seperates the controllers into two variables for convenience.
con0=controllers[0]
con1=controllers[1]

# This try except block releases the kernels hold on the controllers so we can interface with it. If the device has already been detached then it will throw an exception [Errno 2] device not found.  We just ignore that exception since I didn't feel like spending too much time dealing with this and it just confirms that the kernel does not have a handle on the devices. The input to the function is the interface which is 0 for both devices.
try:
	con0.detach_kernel_driver(0)
	con1.detach_kernel_driver(0)
except usb.core.USBError:
	pass

# Now we are setting the configuration for the controllers.  I am just using the default configuration for each motor which is why I pass no arguments.  The call can accept which specific configuration to use.  If the devices are not configured you cannot access them.
con0.set_configuration()
con1.set_configuration()

# This code iterates over some properties of the devices.  I do not use these too much except ep.bEndointAddress which is 0x02 for both of them.  These can be accessed individually using assignments like cfg=con0[0], intf=[(0,0)], ep=intf[2], etc. the direct assignments are useful when testing things real time in the python interpreter.
print 'con0'
print 'bLength', con0.bLength
print 'NumConfigs', con0.bNumConfigurations
print 'DeviceClass', con0.bDeviceClass
for cfg in con0:
    print str(cfg.bConfigurationValue)
    for intf in cfg:
        print '\t' + str(intf.bInterfaceNumber) + ',' + str(intf.bAlternateSetting)
        for ep in intf:
            print '\t\t' + str(ep.bEndpointAddress)

print 'con1'
print 'bLength',con1.bLength
print 'NumConfigs', con1.bNumConfigurations
print 'DeviceClass', con1.bDeviceClass
for cfg in con1:
    print str(cfg.bConfigurationValue)
    for intf in cfg:
        print '\t' + str(intf.bInterfaceNumber) + ',' + str(intf.bAlternateSetting)
        for ep in intf:
            print '\t\t' + str(ep.bEndpointAddress)

# Now I define some messages.  These should be hex arrays.  The values below are just samples from the manual.  I do not know if they are correct.  These need to obey intels endianness so the the hex string 0xC350 would look like [0x50, 0xC3, 0x00, 0x00] in a 4 byte array.  The convention used is outlined in the APT_Communications_Protocol_Rev 6.pdf available on their website.
msg1=[0x23, 0x02, 0x00, 0x00, 0x50, 0x01]
msg2=[0x48, 0x04, 0x01, 0x00, 0xA2, 0x01, 0x01, 0x00, 0x50, 0xC3, 0x00, 0x00]

# Now I am trying to write a message to each of the controllers and print the number of bytes written. The inputs are the endpoint address of each controller which is ep.bEndpointAddress=0x02 for both.
s0=con0.write(0x02, msg1, 0)
s1=con1.write(0x02, msg1, 0)
print s0, s1

t0=con0.write(0x02, msg2, 0)
t1=con1.write(0x02, msg2, 0)
print t0, t1

# Now I am trying to read the buffer for each device as ideally msg2 would have returned some data.  I am reading off 20 bytes from each controller.
w0=con0.read(0x81, 30)
w1=con1.read(0x81, 30)
print w0, w1
