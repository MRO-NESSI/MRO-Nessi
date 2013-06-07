from subprocess import check_call, CalledProcessError, Popen, PIPE

#Colors
colors = {
    'OK'      :'\033[95m',
    'WARNING' :'\033[92m',
    'FAIL'    :'\033[91m',
    'ENDC'    :'\033[0m' ,
}

#Open Yes
yes = Popen('yes', stdout=PIPE).stdout


#Get the character size of the terminal
def getSize():
    return Popen('stty size', shell=True, stdout=PIPE).stdout.read().split()

def taskBatch(msg, tasks):
    print colors['WARNING'] + '==> ' + colors['ENDC'] + msg
    
    for task in tasks:
        task = task.split()
        try:
            check_call(task, stdin=yes)
        except CalledProcessError as e:
            print colors['FAIL']+'\n"'+msg+'" FAILED!'
            print 'Failed on ' + e.cmd + ' with exit status ' + cmd.returncode
            print e.output
            print colors['ENDC']
            exit(1)
    print colors['OK'] + 'Done!' + colors['ENDC']

def main():
    print colors['OK'] + 'Initializing NESSI...' + colors['ENDC']
    batches = []

    batches.append(
        ('Setting up Aptitude...', [
            'add-apt-repository ppa:olebde/astro-precise',
            'apt-get update',
            'apt-get autoremove',
            'apt-get autoclean',
            'apt-get upgrade',
        ]))
    batches.append(
        ('Setting up python basics...', [
            'apt-get install python',
            'apt-get install python-apt',
            'apt-get install python-apt-common',
            'apt-get install python-setuptools',
            'easy_install pip'
        ]))
    batches.append(
        ('Installing compilers (used by pip + good to have)...', [
            'apt-get install gcc',
            'apt-get install g++',
            'apt-get install gfortran',
            'apt-get install make',
        ]))
    batches.append(
        ('Installing python packages...', [
            'apt-get install python-configobj',
            'apt-get install python-numpy',
            'apt-get install python-scipy',
            'apt-get install python-matplotlib',
            'apt-get install python-serial',
            'apt-get install python-usb',
            'apt-get install python-pyds9',
        ]))
    batches.append(
        ('Setting up wxPython...\n(This is experimental...)', [
            'apt-get install python-wxgtk2.8',
            'apt-get install python-wxtools',
            'apt-get install wx2.8-i18n',
            'apt-get install libwxgtk2.8-dev',
            'apt-get install libgtk2.0-dev',
        ]))
    batches.append(
        ('Installing basic utilities...'), [
            'apt-get install gedit',
            'apt-get install emacs',
            'apt-get install zsh',
            'apt-get install bpython',
            'apt-get install curl',
            'apt-get install git',
            'apt-get install awesome',
        ]))

    print colors['OK'] + 'Installing main software...' + colors['ENDC']
    
    for batch in batches:
        taskBatch(batch[0], batch[1])
    
    print colors['OK'] + 'Setting up Oh-My-Zsh' + colors['ENDC']
    subprocess.check_output(
        'curl -L https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh | sh', shell=True) #Maybe should use popen, and pipe...
    
    print colors['OK'] + 'Setting up udev rules...'
    print colors['WARNING'] + '==> ' + colors['ENDC'] + 'Thorlabs...'
    90-thorlabs = '''
#Thorlabs

#Use udevadm info -a -p `udevadm info -q path -n [devpath]`
#to find information about a device. I looked for serial
#numbers. If this device is replaced, find which device
#it is, find the serial number, and replace.

ATTRS{serial}=="83840902", SYMLINK+="ttyREI12", MODE="0666"
ATTRS{serial}=="83841481", SYMLINK+="ttyREI34", MODE="0666"
'''
    f = open('/etc/udev/rules.d/90-thorlabs.rules', 'w')
    f.write(90-thorlabs)
    f.close()
    print colors['OK'] + 'Done!' + colors['ENDC']

    print colors['WARNING'] + '==> ' + colors['ENDC'] + 'Lakeshore...'
    90-lakeshore = '''
#Lakeshore Rules

#Use udevadm info -a -p `udevadm info -q path -n [devpath]`
#to find information about a device. I looked for interface
#If this device is replaced, find which device it is, find
#the serial number, and replace.

ATTRS{interface}=="Model 336 Temperature Controller",SYMLINK+="ttylakeshore",MODE="0666"
'''
    f = open('/etc/udev/rules.d/90-lakeshore.rules', 'w')
    f.write(90-thorlabs)
    f.close()
    print colors['OK'] + 'Done!' + colors['ENDC']

    print colors['WARNING'] + '==> ' + colors['ENDC'] + 'FLI Camera...'
    90-lakeshore = '''
# Finger Lakes Camera

KERNEL=="fliusb*", MODE="666", GROUP="plugdev"
'''
    f = open('/etc/udev/rules.d/90-flicam.rules', 'w')
    f.write(90-thorlabs)
    f.close()
    print colors['OK'] + 'Done!' + colors['ENDC']

    taskBatch('Reloading rules...', ['udevadm control --reload-rules'])


    
if __name__ == '__main__':
    main()
