import pygame
import os
import json
import logging
import subprocess
import urllib3

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

def loadRoms(params=[]):
    menu = []
    if "type" not in params:
        dir= os.listdir(ROMS_PATH)
        for directory in dir:
            if len(os.listdir(os.path.join(ROMS_PATH,directory))) == 0:
                logger.debug("Empty directory %s " % directory)
            else:
                logger.debug("Not empty directory %s, appending to list" % directory)
                element = {}
                element["title"] = "%s" % directory
                element["action"] = 'loadRoms'
                element["params"] = [{
                    'type' : directory
                }]
                menu.append(element)
        element = {}
        element["title"] = "Back"
        element["action"] = 'menu'
        element["external"] = 'main'
        menu.append(element)

    else:
        type = params["type"]
        logger.debug("selected directory is %s " % type)
    return menu


def internetBrowser(params=[]):
    menu = []
    url = ""
    if len(params)>0:
        for key in params:
            logger.debug("str %s" % str(key))
            if 'webpage' in key:
                url = key["webpage"]
    logger.debug("using url: '%s' " % url)
    if len(url)>0:
        http = urllib3.PoolManager()
        r = http.request('GET', url, preload_content=False)
        exit = False
        html = r.data.decode()
        logger.debug(html)
        r.release_conn()

        if len(html)>0:
            container = html[html.find('consoles__wrap">')+len('consoles__wrap">'):]
            container = container[:container.find('<div class="popular-game">')]
            i = 0
            for line in container.split('<a href="'):
                if i > 0:
                    link = url+line[:line.find('"')]
                    img = line[line.find('src="')+len('src="'):]
                    img = img[:img.find('"')]
                    name = line[line.find('console__name">')+len('console__name">'):]
                    name = name[:name.find('<')]
                    element = {}
                    element["title"] = name
                    element["action"] = 'menu'
                    element["external"] = [{'webpage':link}]
                    if len(name)>0:
                        menu.append(element)
                        logger.debug("%s, %s, %s" % (name,img,link) )
                i+=1
            element = {}
            element["title"] = "Back"
            element["action"] = 'menu'
            element["external"] = 'rompages'
            menu.append(element)
        else:
            logger.debug("empty html")
    return menu
