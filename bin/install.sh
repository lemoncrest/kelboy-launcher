#!/bin/bash
sudo apt install -y git python3-setuptools python3-pygame python3-bluez python3-pexpect python3-evdev python3-psutil libpng12-0 bsdtar

cd /tmp

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3 get-pip.py

sudo pip3 install Pillow
