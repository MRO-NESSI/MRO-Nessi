#!/bin/bash

#Colors
BLUE='\x1b[0;34m'
GREEN='\x1b[0;32m'
RED='\x1b[0;31m'
NC='\x1b[0m'
P="${BLUE}=>${GREEN} "

echo -e "Initializing NESSI..."
echo "This script is not fancy... if things fail, they will fail silently."
echo "Attenpt running nessi.py when process is compleat. If depedencies exist, fix accordingly"

#Bring Aptitude up-to-date
echo -e "${P}Setting up Aptitude${NC}"
apt-get update
apt-get autoremove
apt-get autoclean
apt-get install aptitude
aptitude update
aptitude full-upgrade
echo -e "${P}DONE!${NC}"

echo -e "${P} Installing python... ${NC}"
apt-get install python python-apt python-apt-common
echo -e "${P} DONE!${NC}"

echo -e "${P} Setting up python-setuptools${NC}"
apt-get install python-setuptools python-dev
easy_install pip
echo -e "${P} Install bpython...${NC}"
pip install bpython
echo -e "${P} DONE!${NC}"

echo -e "${P} Installing compilers...${NC}"
apt-get install gcc
apt-get install g++
apt-get install gfortran
apt-get install make
echo -e "${P} DONE!${NC}"

echo -e "${P} Python related packages...${NC}"
apt-get install python-serial
apt-get install python-usb
apt-get install python-pyds9
echo -e "${P} DONE!${NC}"

echo -e "${P} Installing python packages via pip... ${NC}"
pip install configobj
pip install wxPython
pip install numpy
apt-get install libxft2
apt-get install libxft-dev
apt-get install libpng12-dev
pip install matplotlib
pip install pyusb
pip install -U pyusb #May already be there...
echo -e "${P} DONE!${NC}"

echo -e "${P} Installing utilities...${NC}"
apt-get install gedit
apt-get install emacs
apt-get install zsh
apt-get install curl
apt-get install awesome
echo -e "${P} DONE! ${NC}"

echo -e "${P} Installing git... ${NC}"
apt-get install git
git configure --global color.ui true
echo -e "${P} DONE! ${NC}"

echo -e "${P} Oh-My-Zsh... ${NC}"
curl -L https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh | sh
echo -e "${P} DONE! ${NC}"

echo -e "${RED} IGNORING FLI DRIVERS, UNTILL FIXED! ${NC}"

echo -e "${P} Cloneing nessi...${NC}"
cd ~/Documents/
git clone git@bitbucket.org:lschmidt/nessi.git
echo -e "${P} DONE! ${NC}"

echo -e "${P} Cleaning... ${NC}"
apt-get autoclean
apt-get autoremove
echo -e "${P} DONE! ${NC}"

echo -e "\n\n${P}HOPEFULLY YOU ARE GOOD TO GO!${NC}"
