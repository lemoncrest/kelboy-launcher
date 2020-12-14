#!/bin/bash

sudo depmod -a
sudo rm -rf /etc/profile.d/depmod.sh
sudo reboot
