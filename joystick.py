# Based on information from:
# https://www.kernel.org/doc/Documentation/input/joystick-api.txt

import os, struct, array, subprocess
from fcntl import ioctl

from core.settings import *
import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
except:
    logger.warning("pending ... pip install RPi.GPIO")
    pass

#FREQ = 65.5689
FREQ = 65.5689

# Iterate over the joystick devices.
logger.debug('Available devices:')

for fn in os.listdir('/dev/input'):
    if fn.startswith('js'):
        logger.debug(('  /dev/input/%s' % (fn)))

# We'll store the states here.
axis_states = {}
button_states = {}

# These constants were borrowed from linux/input.h
axis_names = {
    0x00 : 'x',
    0x01 : 'y',
    0x02 : 'z',
    0x03 : 'rx',
    0x04 : 'ry',
    0x05 : 'rz',
    0x06 : 'trottle',
    0x07 : 'rudder',
    0x08 : 'wheel',
    0x09 : 'gas',
    0x0a : 'brake',
    0x10 : 'hat0x',
    0x11 : 'hat0y',
    0x12 : 'hat1x',
    0x13 : 'hat1y',
    0x14 : 'hat2x',
    0x15 : 'hat2y',
    0x16 : 'hat3x',
    0x17 : 'hat3y',
    0x18 : 'pressure',
    0x19 : 'distance',
    0x1a : 'tilt_x',
    0x1b : 'tilt_y',
    0x1c : 'tool_width',
    0x20 : 'volume',
    0x28 : 'misc',
}

button_names = {
    0x120 : 'trigger',
    0x121 : 'thumb',
    0x122 : 'thumb2',
    0x123 : 'top',
    0x124 : 'top2',
    0x125 : 'pinkie',
    0x126 : 'base',
    0x127 : 'base2',
    0x128 : 'base3',
    0x129 : 'base4',
    0x12a : 'base5',
    0x12b : 'base6',
    0x12f : 'dead',
    0x130 : 'unk1',
    0x131 : 'unk2',
    0x132 : 'T',
    0x133 : 'Z',
    0x134 : 'unk3',
    0x135 : 'unk4',
    0x136 : 'SELECT',
    0x137 : 'START',
    0x138 : 'RIGHT',
    0x139 : 'LEFT',
    0x13a : 'DOWN',
    0x13b : 'UP',
    0x13c : 'Y',
    0x13d : 'X',
    0x13e : 'B',
    0x13f : 'A',
    0x220 : 'dpad_up',
    0x221 : 'dpad_down',
    0x222 : 'dpad_left',
    0x223 : 'dpad_right',

    # XBox 360 controller uses these codes.
    0x2c0 : 'dpad_left',
    0x2c1 : 'dpad_right',
    0x2c2 : 'dpad_up',
    0x2c3 : 'dpad_down',
}

axis_map = []
button_map = []

# Open the joystick device.
fn = '/dev/input/js0'
logger.debug(('Opening %s...' % fn))
jsdev = open(fn, 'rb')

# Get the device name.
#buf = bytearray(63)
buf = array.array('B', [0] * 64)
ioctl(jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
js_name = buf.tostring().rstrip(b'\x00').decode('utf-8')
logger.debug(('Device name: %s' % js_name))

# Get number of axes and buttons.
buf = array.array('B', [0])
ioctl(jsdev, 0x80016a11, buf) # JSIOCGAXES
num_axes = buf[0]

buf = array.array('B', [0])
ioctl(jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
num_buttons = buf[0]

# Get the axis map.
buf = array.array('B', [0] * 0x40)
ioctl(jsdev, 0x80406a32, buf) # JSIOCGAXMAP

for axis in buf[:num_axes]:
    axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
    axis_map.append(axis_name)
    axis_states[axis_name] = 0.0

# Get the button map.
buf = array.array('H', [0] * 200)
ioctl(jsdev, 0x80406a34, buf) # JSIOCGBTNMAP

for btn in buf[:num_buttons]:
    btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
    button_map.append(btn_name)
    button_states[btn_name] = 0

logger.debug(('%d axes found: %s' % (num_axes, ', '.join(axis_map))))
logger.debug(('%d buttons found: %s' % (num_buttons, ', '.join(button_map))))
battery = False
lightLevel = 100
brightness = None
try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(40, GPIO.OUT)
    brightness = GPIO.PWM(40, FREQ)
    brightness.start(0)
    brightness.ChangeDutyCycle(100)
except:
    logger.warning("needs pip library RPi.GPIO")
    pass

# Main event loop
while True:
    evbuf = jsdev.read(8)
    if evbuf:
        time, value, type, number = struct.unpack('IhBB', evbuf)

        if type & 0x80:
             logger.debug("(initial)")

        if type & 0x01:
            button = button_map[number]
            if button:
                button_states[button] = value
                if value:
                    logger.debug(("%s pressed" % (button)))
                else:
                    logger.debug(("%s released" % (button)))

        if type & 0x02:
            axis = axis_map[number]
            if axis:
                fvalue = value / 32767.0
                axis_states[axis] = fvalue
                logger.debug(("%s: %.3f" % (axis, fvalue)))

        if button_states["START"]:
            process = subprocess.run(AUDIO_CONTROL_CMD, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            device = process.stdout
            logger.debug("device is: %s" % device)
            if button_states["UP"]:
                logger.debug("bundle up detected")
                command = 'amixer set %s -- 10+' % device
                os.system(command)
                logger.debug("command %s" % command)
            elif button_states["DOWN"]:
                logger.debug("bundle down detected")
                command = 'amixer set %s -- 10-' % device
                os.system(command)
                logger.debug("command %s" % command)
            elif button_states["LEFT"]:
                logger.debug("bundle down detected")
                command = 'amixer set %s 0' % device
                os.system(command)
                logger.debug("command %s" % command)
            elif button_states["RIGHT"]:
                logger.debug("bundle down detected")
                command = 'amixer set %s 50%%' % device
                os.system(command)
                logger.debug("command %s" % command)
        if button_states["SELECT"] and button_states["UP"]:
            logger.debug("bundle2 up detected")
            logger.debug("showing battery...")
            try:
                process = subprocess.run(BATTERY_PERCENTAGE_CMD, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
                battery = int(process.stdout)
                logger.debug("%s" % str(battery))
            except:
                battery = 0 #"lightning-empty-help"
                level = 0
                pass
            charging = False
            try:
                process = subprocess.run(FUELGAUGE_CURRENT_CMD, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
                charging = int(process.stdout) > 0
                logger.debug("%s" % str(battery))
            except:
                charging = False
                pass
            pwd = os.getcwd()
            if charging:
                level = "lightning-empty-help"
                if(battery>50):
                    level = "lightning-midle"
                    if(battery>=95):
                        level = "lightning-full"
                elif battery>15:
                    level = "lightning-empty"
                command="bin/pngview %s/resources/graphics/battery-%s.png -b 0 -l 300003 -x 290 -y 7 -t 5000 &" % (pwd,level)
            else:
                if(battery>50):
                    level = "75"
                    if(battery<75):
                        level = "50"
                    elif(battery>=95):
                        level = "100"
                elif battery>15:
                    level = "25"
                else:
                    level = "0"
                logger.debug("level is %s" % level)
                command="bin/pngview %s/resources/graphics/battery-%s.png -b 0 -l 300003 -x 290 -y 7 -t 5000 &" % (pwd,level)
            logger.debug("command... %s" % command)
            battery = True
            os.system(command)
            logger.debug("command done")
        if button_states["SELECT"] and button_states["DOWN"]:
            logger.debug("bundle2 down detected")
        if button_states["SELECT"] and button_states["LEFT"]:
            lightLevel = lightLevel - 10 if lightLevel >= 10 else 0
            brightness.ChangeDutyCycle(lightLevel)
            logger.debug("brightness is %s" % lightLevel)
        if button_states["SELECT"] and button_states["RIGHT"]:
            lightLevel = lightLevel + 10 if lightLevel <= 90 else 100
            brightness.ChangeDutyCycle(lightLevel)
            logger.debug("brightness is %s" % lightLevel)

try:
    brightness.ChangeDutyCycle(100)
except:
    pass
