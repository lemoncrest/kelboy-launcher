from core.colors import *

#Constants

WIDTH = 320
HEIGHT = 240

frameRate = 60
margin = 10

screensaverTime = 60000 #milliseconds
FONT_SIZE = 18
FONT_COLOR_ITEM = DARK_GRAY
FONT_TYPE = 'resources/fonts/editundo_var.ttf'
FONT_TYPE_KEYBOARD = 'resources/fonts/zeldadxt_mono.ttf'
FONT_TYPE_KEYBOARDBAR = 'resources/fonts/DejaVuSans.ttf'
LOG_PATH = "/tmp/"
LOG_FILE = "log.txt"
WPA_SUPPLICANT = '/etc/wpa_supplicant/wpa_supplicant.conf'
UPLOAD_SITE = 'https://github.com/lemoncrest/kelboy-launcher/archive/master.zip'
MAX_MENU_ITEMS = 10
BACKGROUND_PICTURE = "start-background.png"

ROMS_PATH = '/home/pi/RetroPie/roms'

FRAMES_IN = 16
FRAMES_OUT = 16

BARSIZE = 25

BATTERY_PERCENTAGE_CMD = 'cat /sys/class/power_supply/max1726x_battery/capacity'

FUELGAUGE_CURRENT_CMD = 'cat /sys/class/power_supply/max1726x_battery/current_now'

RETROARCH_BIN = '/opt/retropie/emulators/retroarch/bin/retroarch'
RETROARCH_CONFIG = '/opt/retropie/configs/gb/retroarch.cfg'

LIB_GBC = '/opt/retropie/libretrocores/lr-gambatte/gambatte_libretro.so'
