from subprocess import check_call, check_output, CalledProcessError, Popen, PIPE, STDOUT
from os import chdir
from os.path import expanduser

#Colors
colors = {
    'OK'      :'\033[95m',
    'WARNING' :'\033[92m',
    'FAIL'    :'\033[91m',
    'ENDC'    :'\033[0m' ,
}

#Open Yes
yes = Popen('yes', stdout=PIPE)

#Get the character size of the terminal
def getSize():
    return map(int, Popen('stty size', shell=True, stdout=PIPE).stdout.read().split())

def taskBatch(msg, tasks):
    print colors['WARNING'] + '==> ' + colors['ENDC'] + msg
    
    n = len(tasks)
    c = 0

    for task in tasks:
        task = task.split()
        print task
        if task[0] == 'cd':
            chdir(expanduser(task[1]))
            c += 1
            print '%i / %i' % (c, n)
            continue
        try:
            check_output(task, stderr=STDOUT, stdin=yes.stdout)
        except CalledProcessError as e:
            print colors['FAIL']+'\n"'+msg+'" FAILED!'
            print 'Failed on ' + str(e.cmd) + ' with exit status ' + str(e.returncode)
            print e.output
            print colors['ENDC']
            yes.kill()
            exit(1)
        c += 1
        print '%i / %i' % (c, n)
    print colors['OK'] + 'Done!' + colors['ENDC']

def main():
    print colors['OK'] + 'Initializing NESSI...' + colors['ENDC']
    batches = []

    batches.append(
        ('Setting up Aptitude...', [
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
            'pip install -U pyusb',
            'pip install -U pywcs',
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
        ('Installing basic utilities...', [
            'apt-get install gedit',
            'apt-get install emacs',
            'apt-get install zsh',
            'apt-get install bpython',
            'apt-get install curl',
            'apt-get install wget',
            'apt-get install git',
            'apt-get install awesome',
            'apt-get install finger'
        ]))

    print colors['OK'] + 'Installing main software...' + colors['ENDC']
    
    for batch in batches:
        taskBatch(batch[0], batch[1])
    
    print colors['OK'] + 'Setting up Oh-My-Zsh' + colors['ENDC']
    try:
        print check_output(
            'curl -L https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh | sh', shell=True) #Maybe should use popen, and pipe...
    except:
        pass
    finally:
        print colors['OK'] + 'Done!' + colors['ENDC']

    print colors['OK'] + 'Setting up udev rules...'
    print colors['WARNING'] + '==> ' + colors['ENDC'] + 'Thorlabs...'
    thorlabs = '''
#Thorlabs

#Use udevadm info -a -p `udevadm info -q path -n [devpath]`
#to find information about a device. I looked for serial
#numbers. If this device is replaced, find which device
#it is, find the serial number, and replace.

ATTRS{serial}=="83840902", SYMLINK+="ttyREI34", MODE="0666"
ATTRS{serial}=="83841481", SYMLINK+="ttyAGR", MODE="0666"
'''
    f = open('/etc/udev/rules.d/90-thorlabs.rules', 'w')
    f.write(thorlabs)
    f.close()
    print colors['OK'] + 'Done!' + colors['ENDC']

    print colors['WARNING'] + '==> ' + colors['ENDC'] + 'Lakeshore...'
    lakeshore = """#Lakeshore Rules

#Use udevadm info -a -p `udevadm info -q path -n [devpath]`
#to find information about a device. I looked for interface
#If this device is replaced, find which device it is, find
#the serial number, and replace.

ATTRS{idVendor}=="1fb9", ATTRS{idProduct}=="0301",  MODE="0666", GROUP="users", SYMLINK+="ttylakeshore"
"""
    f = open('/etc/udev/rules.d/90-lakeshore.rules', 'w')
    f.write(lakeshore)
    f.close()
    print colors['OK'] + 'Done!' + colors['ENDC']

    print colors['WARNING'] + '==> ' + colors['ENDC'] + 'FLI Camera...'
    flicam = """# Finger Lakes Camera

KERNEL=="fliusb*", MODE="666", GROUP="plugdev"
"""
    f = open('/etc/udev/rules.d/90-flicam.rules', 'w')
    f.write(flicam)
    f.close()
    print colors['OK'] + 'Done!' + colors['ENDC']

    taskBatch('Reloading rules...', ['udevadm control --reload-rules'])

    print colors['OK'] + 'Installing kernel headers...'
    uname = check_output(['uname', '-r']).strip()
    taskBatch('Installing kernel headers...', [
            'apt-get install linux-headers-%s' % uname
        ])
    print colors['OK'] + 'Installing PyGuide...'
    taskBatch('Fetching and installing PyGuide...', [
            'rm -rf /tmp/PyGuide-build',
            'mkdir /tmp/PyGuide-build',
            'cd /tmp/PyGuide-build',
            'wget http://www.astro.washington.edu/users/rowen/PyGuide/files/PyGuide_2.2.1.zip -O PyGuide.zip',
            'unzip PyGuide.zip',
            'cd PyGuide_2.2.1',
            'python setup.py build',
            'python setup.py install'
            ])
    print colors['OK'] + 'Setting up pyfli...'
    taskBatch('Downloading/Building fliusb-1.3...', [
            'rm -rf /tmp/pyfli-build',
            'git clone https://github.com/charris/pyfli.git /tmp/pyfli-build',
            'cd /tmp/pyfli-build/fliusb-1.3',
            'make clean',
            'make'
            ])
    print colors['OK'] + 'Installing fliusb...'
    taskBatch('Copying files/depmod...', [
            'mkdir -p /lib/modules/%s/misc' % uname,
            'cp fliusb.ko /lib/modules/%s/misc/' % uname,
            'depmod'
            ])
    taskBatch('Building/Installing pyfli...', [
            'cd /tmp/pyfli-build',
            'python setup.py build',
            'python setup.py install'
            ])
    
    print colors['OK'] + 'Installing NESSI...'
    user_home = check_output(['printenv', 'HOME']).strip()
    taskBatch('Downloading current software...', [
            'mkdir -p %s/NESSI' % user_home,
            'cd %s/NESSI' % user_home,
            'wget https://bitbucket.org/lschmidt/nessi/get/master.tar.gz',
            'tar -xvf master.tar.gz',
            ])

    print colors['OK'] + 'Moving NESSI...'
    try:
        check_output('mv lschmidt* nessi', shell=True)
        user = check_output('who').split()[0]
        check_output('chown %s ./nessi' % user, shell=True)            
    except CalledProcessError as e:
        print e.output
        yes.kill()
        exit(1)

    print colors['OK'] + '<== You done, yo! ==>' + colors['ENDC']

    yes.kill()
    
if __name__ == '__main__':
    main()
