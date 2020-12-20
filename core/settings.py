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

WIDTH = getValue("WIDTH",320,'screen width resolution')
HEIGHT = getValue("HEIGHT",240,'screen height resolution')

FRAMERATE = getValue("FRAMERATE",60,'framerate')
margin = getValue("margin",10,'general margin in pixels')

LOGGING_LEVEL = getValue('LOGGING_LEVEL',logging.ERROR,'for development purpouse use logging.DEBUG or logging.INFO, if not use logging.ERROR')

SCREENSAVER_TIME = getValue("SCREENSAVER_TIME",60000,'trigger for screensaver in milliseconds')
KEY_SLEEP = getValue("KEY_SLEEP",0.02,'time between key is pushed and launcher reacts') #repeat time
KEY_WHILE_SLEEP = getValue("KEY_WHILE_SLEEP",0.1,'time before reacts while key is pressed for repeat action - like up or down')

WIDGET_FRAMETIME = getValue("WIDGET_FRAMETIME",200,'refresh time for widgets')

FONT_SIZE = getValue("FONT_SIZE",18,'default font size')
FONT_COLOR_ITEM = getValue("FONT_COLOR_ITEM",WHITE,'default font color')
FONT_TYPE = getValue("FONT_TYPE",'resources/fonts/editundo_var.ttf','default font type')
FONT_TYPE_KEYBOARD = getValue("FONT_TYPE_KEYBOARD",'resources/fonts/zeldadxt_mono.ttf','default keyboard font type in keys')
FONT_TYPE_KEYBOARDBAR = getValue("FONT_TYPE_KEYBOARDBAR",'resources/fonts/DejaVuSans.ttf','default keyboard font type in string (keys pressed before press enter)')

WPA_SUPPLICANT = getValue("WPA_SUPPLICANT",'/etc/wpa_supplicant/wpa_supplicant.conf','where is the wpa-supplicant in the system, must not be changed')
UPLOAD_SITE = getValue("UPLOAD_SITE",'https://github.com/lemoncrest/kelboy-launcher/archive/master.zip','default github download repository like zip')
MAX_MENU_ITEMS = getValue("MAX_MENU_ITEMS",10,'max number of items in the menus')
BACKGROUND_PICTURE = getValue("BACKGROUND_PICTURE","background-br.png",'this value configures the background image and must be stored in resources/graphics/')

ROMS_PATH = getValue("ROMS_PATH",'/home/pi/RetroPie/roms','default roms path')

FRAMES_IN = getValue("FRAMES_IN",16,'number of frames for pixelate effect (out)')
FRAMES_OUT = getValue("FRAMES_OUT",16,'number of frames for pixelate effect (out)')

EVENT_DELAY_TIME = getValue("EVENT_DELAY_TIME",1000,'default delay time')
HORIZONTAL_MOVEMENT_REFRESH_FACTOR = getValue("HORIZONTAL_MOVEMENT_REFRESH_FACTOR",50,'horizontal text movement effect in selected choice in menus, less is faster')
HORIZONTAL_MOVEMENT_WAIT_TIME = getValue("HORIZONTAL_MOVEMENT_WAIT_TIME",5,'wait time for horizontal effect in seconds')

BARSIZE = getValue("BARSIZE",25,'up barsize (widgets) height in pixels')

BATTERY_PERCENTAGE_CMD = getValue("BATTERY_PERCENTAGE_CMD",'cat /sys/class/power_supply/max1726x_battery/capacity','command for battery value, must not be changed')
FUELGAUGE_CURRENT_CMD = getValue("FUELGAUGE_CURRENT_CMD",'cat /sys/class/power_supply/max1726x_battery/current_now','command for fuelgague status, should not be changed')
BRIGHTNESS_CURRENT_CMD = getValue("BRIGHTNESS_CURRENT_CMD",'cat /sys/class/backlight/kelboy_pwm_backlight/actual_brightness','command for brightness level, must not be changed')
BRIGHTNESS_MAXLEVEL_CMD = getValue("BRIGHTNESS_MAXLEVEL_CMD",'cat /sys/class/backlight/kelboy_pwm_backlight/max_brightness','command for max brightness level, must not be changed')
BRIGHTNESS_SETUP_CMD = getValue("BRIGHTNESS_SETUP_CMD",'/sys/class/backlight/kelboy_pwm_backlight/brightness','command for change brightness level, should not be changed')

AUDIO_CONTROL_CMD = getValue("AUDIO_CONTROL_CMD","amixer | grep control | head -n 1 | awk -F' ' '{ print $4 }'",'command for audio control with amixer')

PICO8_BIN = getValue("PICO8_BIN",'/home/pi/pico-8/pico8','pico8 bin path')

RETROARCH_BIN = getValue("RETROARCH_BIN",'/opt/retropie/emulators/retroarch/bin/retroarch','retroarch bin path')

CONFIG_GB = getValue("CONFIG_GB",'/opt/retropie/configs/gb/retroarch.cfg','gb / gbc configuration')
LIB_GB = getValue("LIB_GB",'/opt/retropie/libretrocores/lr-gambatte/gambatte_libretro.so','lib gb / gbc')

CONFIG_GBA = getValue("CONFIG_GBA",'/opt/retropie/configs/gba/retroarch.cfg','gba configuration')
LIB_GBA = getValue("LIB_GBA",'/opt/retropie/libretrocores/lr-mgba/mgba_libretro.so','lib gba')

CONFIG_MD = getValue("CONFIG_MD",'/opt/retropie/configs/megadrive/retroarch.cfg','megadrive configuration')
LIB_MD = getValue("LIB_MD",'/opt/retropie/libretrocores/lr-genesis-plus-gx/genesis_plus_gx_libretro.so','lib megadrive')

LIB_N64 = getValue("LIB_N64",'/opt/retropie/libretrocores/lr-mupen64plus-next/mupen64plus_next_libretro.so','nintendo 64 configuration')
CONFIG_N64 = getValue("CONFIG_N64",'/opt/retropie/configs/n64/retroarch.cfg','lib nintendo 64')

CONFIG_AMSTRAD = getValue("CONFIG_AMSTRAD",'/opt/retropie/configs/amstradcpc/retroarch.cfg','amstrad configuration')
LIB_AMSTRAD = getValue("LIB_AMSTRAD",'/opt/retropie/libretrocores/lr-caprice32/cap32_libretro.so','lib amstrad')

LIB_NES = getValue("LIB_NES",'/opt/retropie/libretrocores/lr-fceumm/fceumm_libretro.so','nes configuration')
CONFIG_NES = getValue("CONFIG_NES",'/opt/retropie/configs/nes/retroarch.cfg','lib nes')

LIB_SNES = getValue("LIB_SNES",'/opt/retropie/libretrocores/lr-snes9x2010/snes9x2010_libretro.so','snes configuration')
CONFIG_SNES = getValue("CONFIG_SNES",'/opt/retropie/configs/snes/retroarch.cfg','lib snes')
LIB_SNES_2010 = getValue("LIB_SNES_2010",'/opt/retropie/libretrocores/lr-snes9x2010/snes9x2010_libretro.so','lib snes 2010')
