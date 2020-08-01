import pygame
import os
import json
import logging
import subprocess

from core.bluetooth import Bluetooth

from core.settings import *
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=logging.DEBUG)
logger = logging.getLogger(__name__)

def saveWifiConfig(ssid='', pwd=''):
    with open(os.path.join("resources/menus","wifi.json")) as jsonMenu:
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
    process = subprocess.run('wpa_passphrase ' + ssid_fix + ' ' + pwd_fix, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    logger.debug(output)
    if 'network={' in output:
        with open("wpa_supplicant.conf", 'w') as (myfile):
            myfile.write(line_0_default + '\n')
            myfile.write(line_1_default + '\n')
            myfile.write(line_2_default + '\n')
            myfile.write(output)
    else:
        with open("wpa_supplicant.conf", 'w') as (myfile):
            myfile.write(line_0_default + '\n')
            myfile.write(line_1_default + '\n')
            myfile.write(line_2_default + '\n')
    process = subprocess.run('sudo mv wpa_supplicant.conf '+WPA_SUPPLICANT, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    process = subprocess.run('wpa_cli -i wlan0 reconfigure', shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    #p = subprocess.Popen('wpa_cli -i wlan0 reconfigure', stdout=subprocess.PIPE, shell=True)
    #output, err = p.communicate()
    #p.wait()
    self.is_connecting = True

def scanBluetoothDevices():
    logger.debug("Init bluetooth...")
    bl = Bluetooth()
    logger.debug("Scanning for 10 seconds...")
    devices = bl.scan_devices()
    menu = []
    #now put in a list...
    for device in devices:
        deviceName = device["name"]
        deviceValue = device["address"]
        element = {}
        element["title"] = deviceValue
        element["action"] = 'connectBluetooth'
        menu.append(element)
    #back
    element["title"] = "Back"
    element["action"] = 'menu'
    element["external"] = 'settings'
    menu.append(element)
    return menu

def connectToBluetooth():
    logger.debug("Init bluetooth...")
    bl = Bluetooth()
    logger.debug("Scanning for 10 seconds...")
    devices = bl.scan_devices()
    target = None #"34:DF:2A:66:66:22"
    for device in devices:
        deviceName = device["name"]
        deviceValue = device["address"]
        if deviceValue == '34:DF:2A:66:66:22': #AKG N700NCM2
            target = deviceValue
            logger.debug("found target %s %s " % (target,deviceName))
        else:
            logger.debug("discarting  %s %s " % (deviceValue,deviceName))

    if target != None:
        logger.debug("pairing...")
        #pair
        bl.pair(target)
        logger.debug("connecting...")
        #connect
        bl.connect(target)
    else:
        logger.debug("not found, not connected")
