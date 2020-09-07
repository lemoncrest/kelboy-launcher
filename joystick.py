# Based on information from:
# https://www.kernel.org/doc/Documentation/input/joystick-api.txt

import os, struct, array
from fcntl import ioctl

from core.settings import *
import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

        if button_states["START"] and button_states["UP"]:
            logger.debug("bundle up detected")
            os.system('amixer set PCM -- 10+')
        if button_states["START"] and button_states["DOWN"]:
            logger.debug("bundle down detected")
            os.system('amixer set PCM -- 10-')
        if button_states["START"] and button_states["LEFT"]:
            logger.debug("bundle down detected")
            os.system('amixer set PCM 0')
        if button_states["START"] and button_states["RIGHT"]:
            logger.debug("bundle down detected")
            os.system('amixer set PCM 50%')
        if button_states["SELECT"] and button_states["UP"]:
            logger.debug("bundle2 up detected")
            if battery:
                #command = "killall pngview"
                #process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
                out = check_output("ps aux | grep pngview | awk '{ print $2 }'", shell=True)
                nums = out.decode('ascii').split('\n')
                for num in nums:
                    i += 1
                    if i == 2:
                        killid = num
                        command2 = "sudo kill %s" %killid
                        subprocess.run(command2, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
                battery = False
            else:
                command = 'cat /sys/class/power_supply/max1726x_battery/capacity'
                try:
                    process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
                    battery = int(process.stdout)
                except:
                    battery = 0 #"lightning-empty-help"
                    level = 0
                    pass
                if not charging:
                    if(battery>50):
                        level = "75"
                        if(battery<75):
                            level = "50"
                        elif(battery>=95):
                            level = "100"
                    elif battery>0:
                        level = "25"
                command="sudo bin/pngview resources/graphics/battery-%s.png -b 0 -l 300003 -x 290 -y 7 &" % level
                process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
                battery = True
        if button_states["SELECT"] and button_states["DOWN"]:
            logger.debug("bundle2 down detected")
