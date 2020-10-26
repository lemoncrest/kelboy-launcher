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
SETTINGS_FILE = os.path.join(SETTINGS_PATH,'settings.json')

def getValue(key,default,description=''):
    if not os.path.isdir(SETTINGS_PATH):
        os.makedirs(SETTINGS_PATH)
    if not os.path.isfile(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'w') as json_file:
            dummy_setting = {}
            element = {}
            element['value'] = 320
            element['default'] = 320
            element['description'] = "default width resolution"
            dummy_setting["WIDTH"] = element
            json.dump(dummy_setting, json_file, indent=4)
    value = ""
    with open(SETTINGS_FILE) as json_file:
        data = json.load(json_file)
        if key in data and 'value' in data[key]:
            value = data[key]['value']
            logger.debug("obtained %s for %s with default %s" % (value,key,default))
        else:
            logger.debug("setting %s for %s with %s" % (key,default,description) )
            setValue(key,default,default,description,data)
            value = default
    return value

def setValue(key,value,default='',description='',data=None):
    if not data:
        with open(SETTINGS_FILE, 'w') as json_file:
            data = json.load(json_file)
            if description == '' and key in data and 'description' in data[key]:
                description = data[key]['description']
            if default == '' and key in data and 'default' in data[key]:
                default = data[key]['default']
    element = {}
    element['value'] = value
    element['default'] = default
    element['description'] = description
    data[key] = element
    with open(SETTINGS_FILE, 'w') as outfile:
        json.dump(data, outfile, indent=4)
        logger.debug("stored %s setting with value %s for %s with %s" % (key,value,default,description) )

#Constants (settings)

WIDTH = getValue("WIDTH",320)
HEIGHT = getValue("HEIGHT",240)

FRAMERATE = getValue("FRAMERATE",60)
margin = getValue("margin",10)

SCREENSAVER_TIME = getValue("SCREENSAVER_TIME",60000) #milliseconds
KEY_SLEEP = getValue("KEY_SLEEP",0.02) #repeat time
KEY_WHILE_SLEEP = getValue("KEY_WHILE_SLEEP",0.1)

WIDGET_FRAMETIME = getValue("WIDGET_FRAMETIME",200)

FONT_SIZE = getValue("FONT_SIZE",18)
FONT_COLOR_ITEM = getValue("FONT_COLOR_ITEM",WHITE)
FONT_TYPE = getValue("FONT_TYPE",'resources/fonts/editundo_var.ttf')
FONT_TYPE_KEYBOARD = getValue("FONT_TYPE_KEYBOARD",'resources/fonts/zeldadxt_mono.ttf')
FONT_TYPE_KEYBOARDBAR = getValue("FONT_TYPE_KEYBOARDBAR",'resources/fonts/DejaVuSans.ttf')

WPA_SUPPLICANT = getValue("WPA_SUPPLICANT",'/etc/wpa_supplicant/wpa_supplicant.conf')
UPLOAD_SITE = getValue("UPLOAD_SITE",'https://github.com/lemoncrest/kelboy-launcher/archive/master.zip')
MAX_MENU_ITEMS = getValue("MAX_MENU_ITEMS",10)
BACKGROUND_PICTURE = getValue("BACKGROUND_PICTURE","background-br.png")

ROMS_PATH = getValue("ROMS_PATH",'/home/pi/RetroPie/roms')

FRAMES_IN = getValue("FRAMES_IN",16)
FRAMES_OUT = getValue("FRAMES_OUT",16)

EVENT_DELAY_TIME = getValue("EVENT_DELAY_TIME",1000)
HORIZONTAL_MOVEMENT_REFRESH_FACTOR = getValue("HORIZONTAL_MOVEMENT_REFRESH_FACTOR",50) #less is faster
HORIZONTAL_MOVEMENT_WAIT_TIME = getValue("HORIZONTAL_MOVEMENT_WAIT_TIME",5) #in seconds

BARSIZE = getValue("BARSIZE",25)

BATTERY_PERCENTAGE_CMD = getValue("BATTERY_PERCENTAGE_CMD",'cat /sys/class/power_supply/max1726x_battery/capacity')
FUELGAUGE_CURRENT_CMD = getValue("FUELGAUGE_CURRENT_CMD",'cat /sys/class/power_supply/max1726x_battery/current_now')

AUDIO_CONTROL_CMD = getValue("AUDIO_CONTROL_CMD","amixer | grep control | head -n 1 | awk -F' ' '{ print $4 }'")

PICO8_BIN = getValue("PICO8_BIN",'/home/pi/pico-8/pico8')

RETROARCH_BIN = getValue("RETROARCH_BIN",'/opt/retropie/emulators/retroarch/bin/retroarch')

CONFIG_GB = getValue("CONFIG_GB",'/opt/retropie/configs/gb/retroarch.cfg','gb / gbc')
LIB_GB = getValue("LIB_GB",'/opt/retropie/libretrocores/lr-gambatte/gambatte_libretro.so','lib gb / gbc')

CONFIG_GBA = getValue("CONFIG_GBA",'/opt/retropie/configs/gba/retroarch.cfg','gba')
LIB_GBA = getValue("LIB_GBA",'/opt/retropie/libretrocores/lr-mgba/mgba_libretro.so','lib gba')

CONFIG_MD = getValue("CONFIG_MD",'/opt/retropie/configs/megadrive/retroarch.cfg','megadrive')
LIB_MD = getValue("LIB_MD",'/opt/retropie/libretrocores/lr-genesis-plus-gx/genesis_plus_gx_libretro.so','lib megadrive')

LIB_N64 = getValue("LIB_N64",'/opt/retropie/libretrocores/lr-mupen64plus-next/mupen64plus_next_libretro.so','nintendo 64')
CONFIG_N64 = getValue("CONFIG_N64",'/opt/retropie/configs/n64/retroarch.cfg','lib nintendo 64')

CONFIG_AMSTRAD = getValue("CONFIG_AMSTRAD",'/opt/retropie/configs/amstradcpc/retroarch.cfg','amstrad')
LIB_AMSTRAD = getValue("LIB_AMSTRAD",'/opt/retropie/libretrocores/lr-caprice32/cap32_libretro.so','lib amstrad')

LIB_NES = getValue("LIB_NES",'/opt/retropie/libretrocores/lr-fceumm/fceumm_libretro.so','nes')
CONFIG_NES = getValue("CONFIG_NES",'/opt/retropie/configs/nes/retroarch.cfg','lib nes')

LIB_SNES = getValue("LIB_SNES",'/opt/retropie/libretrocores/lr-snes9x2010/snes9x2010_libretro.so','snes')
CONFIG_SNES = getValue("CONFIG_SNES",'/opt/retropie/configs/snes/retroarch.cfg','lib snes')
LIB_SNES_2010 = getValue("LIB_SNES_2010",'/opt/retropie/libretrocores/lr-snes9x2010/snes9x2010_libretro.so','lib snes 2010')
