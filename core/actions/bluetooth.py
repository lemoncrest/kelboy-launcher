import os
import json
import logging
from core.settings import *
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=logging.DEBUG)
logger = logging.getLogger(__name__)

from core.bluetooth import Bluetooth

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
        element["action"] = 'function'
        element["external"] = 'connectBluetooth'
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
    if type(params) is list:
        logger.debug("list")
        for element in params:
            logger.debug("ele %s" % str(element))
            if "target" in element:
                target = element["target"]
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
        bl.trust_device(target)
        #connect
        bl.connect(target)
        logger.debug("connect done...")
    else:
        logger.debug("not found, not connected")

    bl.exit()

def turnOffBluetooth(params=[]):
    logger.debug("Turning off bluetooth...")
    bl = Bluetooth()
    bl.off()

def turnOnBluetooth(params=[]):
    logger.debug("Turning on bluetooth...")
    bl = Bluetooth()
    bl.on()

def removeBluetooth(params=[]):
    logger.debug("removing bluetooth...")
    bl = Bluetooth()
    devices = bl.get_paired_devices()
    menu = []
    #now put in a list...
    for device in devices:
        deviceName = device["name"]
        deviceValue = device["mac_address"]
        element = {}
        element["title"] = "%s - %s" % (deviceValue, deviceName)
        element["action"] = 'function'
        element["external"] = 'deleteBluetooth'
        element["params"] = [{
            'target' : device["mac_address"]
        }]
        menu.append(element)
    #back
    element = {}
    element["title"] = "Back"
    element["action"] = 'menu'
    element["external"] = 'bluetooth'
    menu.append(element)
    return menu

def deleteBluetooth(params=[]):
    target = None
    if type(params) is list:
        logger.debug("list")
        for element in params:
            logger.debug("ele %s" % str(element))
            if "target" in element:
                target = element["target"]

    if target != None:
        bl = Bluetooth()
        bl.remove(target)
