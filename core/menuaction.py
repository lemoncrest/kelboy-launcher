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

def loadRoms(params=[]): #TODO launch emulationstation configurations by path
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
    text = ""
    final = False
    if len(params)>0:
        for key in params:
            logger.debug("str %s" % str(key))
            if 'webpage' in key:
                url = key["webpage"]
            if 'final' in key:
                final = key["final"]
            if 'text' in key:
                text = key["text"]
    logger.debug("using url: '%s' " % url)
    if len(url)>0:
        http = urllib3.PoolManager()
        if final:
            logger.debug("transforming link %s to final link..." % (url))
            url = url.replace('/roms/','/download/roms/')
        elif len(text)>0 and '%' in url:
            logger.debug("search detected")
            url = url % text
            logger.debug("new url is: %s" % url)
        r = http.request('GET', url, preload_content=False)
        exit = False
        html = r.data.decode()
        r.release_conn()
        if len(html)>0:
            if not final:
                if '<form class="filter" action="/roms/platforms-search">' in html:

                    logger.debug("consoles wrap")
                    container = html[html.find('<form class="filter" action="/roms/platforms-search">')+len('<form class="filter" action="/roms/platforms-search">'):]
                    container = container[:container.find('</table>')]
                    i = 0

                    #first search
                    element = {}
                    link = url[0:url.rfind('/')+1]
                    logger.debug("link %s " % link)
                    link = link+'search?name=%s'
                    logger.debug("link2 %s " % link)
                    element["title"] = "Search"
                    element["action"] = 'function-text'
                    element["external"] = 'internetBrowser'
                    element["params"] = [{'webpage':link, 'final': False}]
                    menu.append(element)

                    for line in container.split('<a href="'):
                        if i > 0:
                            link = line[:line.find('"')]
                            name = line[line.find('">')+len('">'):]
                            name = name[:name.find('<')]
                            element = {}
                            element["title"] = name
                            element["action"] = 'function'
                            element["external"] = 'internetBrowser'
                            element["params"] = [{'webpage':link, 'final': False}]
                            if len(name)>0:
                                menu.append(element)
                                logger.debug("%s, %s" % (name,link) )
                        i+=1
                elif '<div class="results">' in html or '<h1 class="is-medium i-mb-15">Search Result for ' in html:
                    if '<h1 class="is-medium i-mb-15">Search Result for ' in html:
                        container = html[html.find('<table class="table">')+len('<table class="table">'):]
                    else:
                        logger.debug('<div class="results">')
                        container = html[html.find('<div class="results">')+len('<div class="results">'):]

                    container = container[:container.find('</table>')]
                    splitter = '<a href="'
                    i = 0
                    for line in container.split(splitter):
                        if i > 0:
                            logger.debug("inside2...")
                            link = line[:line.find('"')]
                            logger.debug("inside3...")
                            name = line[line.find('">')+len('">'):]
                            logger.debug("inside4...")
                            name = name[:name.find('<')]
                            logger.debug("extracted info...")
                            element = {}
                            element["title"] = name.replace('&#039;',"'")
                            element["action"] = 'function'
                            element["external"] = 'internetBrowser'
                            element["params"] = [{'webpage':link, 'final': True}]
                            logger.debug("appending...")
                            if len(name)>0:
                                menu.append(element)
                                logger.debug("%s, %s" % (link,name) )
                            else:
                                logger.debug("discarting one...")
                        i+=1
                        logger.debug(i)
                else:
                    logger.debug("ELSE result...")

                element = {}
                element["title"] = "Back"
                element["action"] = 'menu'
                element["external"] = 'rompages'
                menu.append(element)
            else:
                logger.debug("final link...")
                link = html[html.find('<a class="wait__link" href="')+len('<a class="wait__link" href="'):]
                link = link[:link.find('"')]
                logger.debug("final url is: %s" % (link) )
                url2 = url.lower()
                if 'gameboy-advance' in url2:
                    subtype = 'gba'
                elif 'super-nintendo' in url2:
                    subtype = 'snes'
                elif 'nintendo-ds' in url2:
                    subtype = 'nds'
                elif 'gameboy-color' in url2:
                    subtype = 'gbc'
                elif 'gameboy' in url2:
                    subtype = 'gb'
                elif 'nintendo-64' in url2:
                    subtype = 'n64'
                elif 'nintendo' in url2:
                    subtype = 'nes'
                elif 'playstation-portable' in url2:
                    subtype = 'psp'
                elif 'playstation-2' in url2:
                    subtype = 'psx2'
                elif 'playstation' in url2:
                    subtype = 'psx'
                elif 'gamecube' in url2:
                    subtype = 'gc'
                elif 'nintendo-wii' in url2:
                    subtype = 'wii'
                elif 'mame' in url2:
                    subtype = 'arcade/mame2003'
                    #subtype = 'mame-libretro/mame2003'
                elif 'dreamcast' in url2:
                    subtype = 'dreamcast'
                elif 'sega-genesis' in url2:
                    subtype = 'genesis'
                elif 'atari-2600' in url2:
                    subtype = 'atari2600'
                elif 'atari-5200' in url2:
                    subtype = 'atari5200'
                elif 'atari-7800' in url2:
                    subtype = 'atari7800'
                elif 'neo-geo' in url2:
                    subtype = 'neogeo'
                elif 'microsoft-xbox' in url2:
                    subtype = 'xbox'

                out = ROMS_PATH+"/"+subtype+"/"
                element = {}
                element["title"] = "Back"
                element["action"] = 'command-exit'
                element["external"] = 'wget %s -P %s' %(link,out)
                return element
        else:
            logger.debug("empty html")
    logger.debug("returning menu...")
    return menu
