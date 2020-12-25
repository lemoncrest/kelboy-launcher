import os
import json
import logging
from core.wifi import Wifi
from core.settings import *
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)

def saveWifiConfig(params=[]):
    logger.debug("starting save wifi config...")
    ssid=''
    pwd=''
    '''
    if len(params) > 0:
        if type(params) is dict:
            logger.debug("dict")
            element = params
            if "ssid" in element:
                logger.debug("%s" % str(element))
                ssid = element["ssid"]
                logger.debug("target ssid %s" % (ssid))
    '''
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
    wifi.buildWpaSupplicantAndConnect(ssid=ssid,pwd=pwd)

def saveWifiSSID(params=[]):
    '''
    {
        "action": "param",
        "external": "text-config",
        "name": "ssid",
        "title": "Network name",
        "value": "",
        "visible": "true"
    }
    '''
    '''
    with open(os.path.join("resources/menus/wifi.json")) as jsonMenu:
        menu = json.load(jsonMenu)
        for element in menu:
            if "name" in element and element["name"] == self.lastMenuParam:
                element["value"] = buffer

    with open(os.path.join(os.getcwd(),"resources/menus/wifi.json"),"w") as jsonMenu:
        json.dump(menu, jsonMenu, indent=4, sort_keys=True)
    '''
    ssid=''
    logger.debug(str(type(params)))
    if type(params) is list:
        logger.debug("list")
        for element in params:
            logger.debug("ele %s" % str(element))
            if "ssid" in element:
                logger.debug("%s" % str(element))
                ssid = element["ssid"]
                logger.debug("target ssid %s" % (ssid))
    if len(ssid)>0:
        with open(os.path.join("resources/menus","wifi.json")) as jsonMenu:
            settings = json.load(jsonMenu)
        for element in settings:
            if 'name' in element and element["name"] == 'ssid':
                element["value"] = ssid
        #now save settings
        with open(os.path.join(os.getcwd(),"resources/menus/wifi.json"),"w") as jsonMenu:
            json.dump(settings, jsonMenu, indent=4, sort_keys=True)
        logger.debug("saved!")
        #TODO launch password keyboard
        '''
        element = {}
        element["external-keyboard"] = "saveWifiPWD"
        element["params"] = [{
            'pwd': element["title"]
        }]
        return element
        '''
        return settings

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
        element["external"] = 'saveWifiSSID'
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
