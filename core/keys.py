import os
import json
from core.colors import *

LOG_PATH = "/tmp/"
LOG_FILE = "log.txt"

#functions for settings
import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=logging.DEBUG)
logger = logging.getLogger(__name__)

SETTINGS_PATH = '/home/pi/.kelboy-launcher/'
JOYSTICK_FILE = os.path.join(SETTINGS_PATH,'joystick.json')

def getKeys():
    #if not exists create new empty one
    if not os.path.isdir(SETTINGS_PATH):
        os.makedirs(SETTINGS_PATH)
    if not os.path.isfile(JOYSTICK_FILE):
        addProcess("pico8")
    value = []
    with open(JOYSTICK_FILE) as json_file:
        value = json.load(json_file)
    return value

def addProcess(process,force=False):
    defaultKeys = []
    try:
        with open(JOYSTICK_FILE, 'r') as json_file:
            try:
                defaultKeys = json.load(json_file)
            except:
                logger.debug("FAIL!, empty")
                pass
            found = False
            for element in defaultKeys:
                if element and 'process' in element and element['process'] == process:
                    found = True #discarting create if exists
                    logger.debug("FOUND!")
                    if force:
                        logger.debug("FORCE REPLACE")
                        element["keys"] = []
            if not found:
                logger.debug("NOT FOUND")
                newElement = {}
                newElement["process"] = process
                newElement["keys"] = []
                defaultKeys.append(newElement)
    except Exception as ex:
        logger.debug(str(ex))
        newElement = {}
        newElement["process"] = process
        newElement["keys"] = []
        defaultKeys.append(newElement)
        pass
    with open(JOYSTICK_FILE,'w') as json_file:
        json.dump(defaultKeys, json_file, indent=4)

def addKey(process,key,values=[],replace=False):

    with open(JOYSTICK_FILE, 'r') as json_file:
        data = json.load(json_file)

        for element in data:
            if 'process' in element and element['process'] == process:
                #found process, now extract keys
                found = False
                for assigned in element["keys"]:
                    if 'key' in assigned and assigned['key'] == key:
                        #found key, now refresh
                        found = True
                        if replace:
                            assigned["callback"] = values

                if not found:
                    #not found so needs to be appended
                    element["keys"].append({"key":key,"callback":values})

    with open(JOYSTICK_FILE, 'w') as outfile:
        json.dump(data, outfile, indent=4)
        logger.debug("stored %s key with values %s for %s" % (key,str(values),process) )

    return key

#default configuration

addProcess("pico8")
addKey("pico8","UP",["KEY_UP"])
addKey("pico8","DOWN",["KEY_DOWN"])
addKey("pico8","LEFT",["KEY_LEFT"])
addKey("pico8","RIGHT",["KEY_RIGHT"])
addKey("pico8","A",["KEY_X"])
addKey("pico8","B",["KEY_C"])
addKey("pico8","X",["KEY_S"])
addKey("pico8","START",["KEY_ENTER"])
addKey("pico8","SELECT",["KEY_LEFTCTRL","KEY_Q"])

addProcess("mpv")
addKey("mpv","UP",["KEY_UP"])
addKey("mpv","DOWN",["KEY_DOWN"])
addKey("mpv","LEFT",["KEY_LEFT"])
addKey("mpv","RIGHT",["KEY_RIGHT"])
addKey("mpv","A",["KEY_SPACE"])
addKey("mpv","B",["KEY_Q"])

#load configurations from configuration file to KEYS
KEYS = getKeys();
