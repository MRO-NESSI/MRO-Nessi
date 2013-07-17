How to use NESSI
================

This will contain a step by step rundown of how to use the NESSI
software, as well as set up various components of the system.

Getting Started
---------------

First step, of course, is to install all relevant software. This can be
done by running the following command:

.. code-block:: bash

    curl https://bitbucket.org/lschmidt/nessi/raw/7e988675ea60da02740e70d84a1fcebeb21ac437/nessisetup.py > setup.py
    sudo python setup.py

This will assume an Debian/Ubuntu system (NESSI was developed on Ubuntu 13.1,
and no support is guarantied for any other distribution).

Running this script will install all dependencies, as well as a number
of development tools and utilities. It is intended to setup whatever
computer is controlling NESSI in a controlled and repeatable manner.

When the script is done running, there should be a directory labeled NESSI
in the users home folder. In order to run the NESSI software:

.. code-block:: bash

    cd ~/Documents/nessi
    ./main.py
