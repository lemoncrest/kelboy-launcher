from core.colors import *

#Constants

WIDTH = 320
HEIGHT = 240

FRAMERATE = 60
margin = 10

SCREENSAVER_TIME = 60000 #milliseconds
KEY_SLEEP = 0.02 #repeat time
KEY_WHILE_SLEEP = 0.1

WIDGET_FRAMETIME = 200

FONT_SIZE = 18
FONT_COLOR_ITEM = WHITE
FONT_TYPE = 'resources/fonts/editundo_var.ttf'
FONT_TYPE_KEYBOARD = 'resources/fonts/zeldadxt_mono.ttf'
FONT_TYPE_KEYBOARDBAR = 'resources/fonts/DejaVuSans.ttf'
LOG_PATH = "/tmp/"
LOG_FILE = "log.txt"
WPA_SUPPLICANT = '/etc/wpa_supplicant/wpa_supplicant.conf'
UPLOAD_SITE = 'https://github.com/lemoncrest/kelboy-launcher/archive/master.zip'
MAX_MENU_ITEMS = 10
BACKGROUND_PICTURE = "background-br.png"

ROMS_PATH = '/home/pi/RetroPie/roms'

FRAMES_IN = 16
FRAMES_OUT = 16

EVENT_DELAY_TIME = 1000
HORIZONTAL_MOVEMENT_REFRESH_FACTOR = 50 #less is faster
HORIZONTAL_MOVEMENT_WAIT_TIME = 5 #in seconds

BARSIZE = 25

BATTERY_PERCENTAGE_CMD = 'cat /sys/class/power_supply/max1726x_battery/capacity'
FUELGAUGE_CURRENT_CMD = 'cat /sys/class/power_supply/max1726x_battery/current_now'

AUDIO_CONTROL_CMD = "amixer | grep control | head -n 1 | awk -F' ' '{ print $4 }'"

PICO8_BIN = '/home/pi/pico-8/pico8'

RETROARCH_BIN = '/opt/retropie/emulators/retroarch/bin/retroarch'

#gb / gbc
CONFIG_GB = '/opt/retropie/configs/gb/retroarch.cfg'
LIB_GB = '/opt/retropie/libretrocores/lr-gambatte/gambatte_libretro.so'
#gba
CONFIG_GBA = '/opt/retropie/configs/gba/retroarch.cfg'
LIB_GBA = '/opt/retropie/libretrocores/lr-mgba/mgba_libretro.so'
#megadrive
CONFIG_MD = '/opt/retropie/configs/megadrive/retroarch.cfg'
LIB_MD = '/opt/retropie/libretrocores/lr-genesis-plus-gx/genesis_plus_gx_libretro.so'
#nintendo 64
LIB_N64 = '/opt/retropie/libretrocores/lr-mupen64plus-next/mupen64plus_next_libretro.so'
CONFIG_N64 = '/opt/retropie/configs/n64/retroarch.cfg'
#amstrad
CONFIG_AMSTRAD = '/opt/retropie/configs/amstradcpc/retroarch.cfg'
LIB_AMSTRAD = '/opt/retropie/libretrocores/lr-caprice32/cap32_libretro.so'
#nes
LIB_NES = '/opt/retropie/libretrocores/lr-fceumm/fceumm_libretro.so'
CONFIG_NES = '/opt/retropie/configs/nes/retroarch.cfg'
#snes
LIB_SNES = '/opt/retropie/libretrocores/lr-snes9x2010/snes9x2010_libretro.so'
CONFIG_SNES = '/opt/retropie/configs/snes/retroarch.cfg'

LIB_SNES_2010 = '/opt/retropie/libretrocores/lr-snes9x2010/snes9x2010_libretro.so'
