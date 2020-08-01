import pygame
import os
import json
import logging
import subprocess

from core.bluetooth import Bluetooth
from core.wifi import Wifi
from core.settings import *
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=logging.DEBUG)
logger = logging.getLogger(__name__)

def saveWifiConfig(params=[]):
    logger.debug("starting save wifi config...")
    ssid=''
    pwd=''
    if len(params) > 0:
        element = params[0]
        if "ssid" in element:
            ssid = element["ssid"]
            logger.debug("target ssid %s" % (ssid))

    #read params
    with open(os.path.join("resources/menus","wifi.json")) as jsonMenu:
        menu = json.load(jsonMenu)
        for element in menu:
            if "name" in element:
                if element["name"] == "ssid" and ssid == '':
                    ssid = element["value"]
                elif element["name"] == "pass" and pwd == '':
                    pwd = element["value"]

    logger.debug("ssid %s and pass %s" % (ssid,pwd))
    wifi = Wifi()
    wifi.buildWpaSupplicantAndConnect()

def scanWifi(params=[]):
    wifi = Wifi()
    networks = wifi.scan_networks()
    logger.debug("found %s networks" % str(len(networks)))
    menu = []
    #now put in a list...
    for network in networks:
        networkName = network["name"]
        element = {}
        element["title"] = "%s" % (networkName)
        element["action"] = "function"
        element["external"] = 'saveWifiConfig'
        element["params"] = [{
            'ssid': element["title"]
        }]
        menu.append(element)
    #back
    element = {}
    element["title"] = "Back"
    element["action"] = 'menu'
    element["external"] = 'settings'
    menu.append(element)
    return menu

def scanBluetoothDevices(params=[]):
    logger.debug("Init bluetooth...")
    bl = Bluetooth()
    logger.debug("Scanning for 10 seconds...")
    devices = bl.get_devices()
    #devices = bl.scan_devices()
    #bl.exit()
    menu = []
    #now put in a list...
    for device in devices:
        deviceName = device["name"]
        deviceValue = device["address"]
        element = {}
        element["title"] = "%s - %s" % (deviceValue, deviceName)
        element["action"] = 'connectBluetooth'
        element["params"] = [{
            'target' : device["address"],
            'name' : device["name"]
        }]
        menu.append(element)
    #back
    element = {}
    element["title"] = "Back"
    element["action"] = 'menu'
    element["external"] = 'settings'
    menu.append(element)
    return menu

def connectBluetooth(params=[]):
    logger.debug("Init bluetooth...")
    bl = Bluetooth()
    logger.debug("connecting...")
    target = None
    name = None
    if "address" in params:
        target = params["address"]
    else: #search stored address
        with open(os.path.join("resources/menus","bluetooth.json")) as jsonMenu:
            menu = json.load(jsonMenu)
            for element in menu:
                if "external" in element:
                    if element["external"] == "connectBluetooth":
                        params = element["params"]
                        if "target" in params:
                            target = params["target"]
                        if "name" in params: #TODO
                            name = params["name"]

    if target != None:
        logger.debug("pairing %s..." % target)
        #pair
        bl.pair(target)
        logger.debug("connecting %s..." % target)
        #connect
        bl.connect(target)
    else:
        logger.debug("not found, not connected")

    bl.exit()
