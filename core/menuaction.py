import pygame
import os
import json
import logging
import subprocess

from core.settings import *
logging.basicConfig(filename=os.path.join(LOG_PATH, "log.txt"),level=logging.DEBUG)
logger = logging.getLogger(__name__)

def saveWifiConfig(ssid='', pwd=''):
    with open(os.path.join(os.getcwd(),"resources/menus/wifi.json")) as jsonMenu:
        menu = json.load(jsonMenu)
        for element in menu:
            if "name" in element:
                if element["name"] == "ssid":
                    ssid = element["value"]
                elif element["name"] == "pass":
                    pwd = element["value"]

    logger.debug("ssid %s and pass %s" % (ssid,pwd))

    line_0_default = 'country=ES'
    line_1_default = 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev'
    line_2_default = 'update_config=1'
    ssid_fix = ssid
    ssid_fix = ssid_fix.replace(' ', '\\ ')
    ssid_fix = ssid_fix.replace("'", '\'')
    pwd_fix = pwd
    pwd_fix = pwd_fix.replace(' ', '\\ ')
    pwd_fix = pwd_fix.replace("'", '\'')
    p = subprocess.Popen('wpa_passphrase ' + ssid_fix + ' ' + pwd_fix, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p.wait()
    if 'network={' in output:
        with open(WPA_SUPPLICANT, 'w') as (myfile):
            myfile.write(line_0_default + '\n')
            myfile.write(line_1_default + '\n')
            myfile.write(line_2_default + '\n')
            myfile.write(output)
    else:
        with open(WPA_SUPPLICANT, 'w') as (myfile):
            myfile.write(line_0_default + '\n')
            myfile.write(line_1_default + '\n')
            myfile.write(line_2_default + '\n')
    p = subprocess.Popen('wpa_cli -i wlan0 reconfigure', stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p.wait()
    self.is_connecting = True
