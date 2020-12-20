# Based on information from:
# https://www.kernel.org/doc/Documentation/input/joystick-api.txt

import os, sys, struct, array, subprocess
import _thread as thread
import time
from subprocess import check_output
from fcntl import ioctl
from evdev import UInput, AbsInfo, InputDevice, uinput, ecodes as e

from PIL import Image, ImageDraw

import psutil

from core.keys import *

from core.settings import *
import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)

try:
    #just for old people who don't want to upgrade to a newer kernel
    import RPi.GPIO as GPIO
except:
    logger.warning("pending ... pip install RPi.GPIO")
    pass

FREQ = 65.5689 #old algorithm

# Iterate over the joystick devices.
logger.debug('Available devices:')

for fn in os.listdir('/dev/input'):
    logger.debug("found %s input device" % str(fn))
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
try:
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
except Exception as ex:
    logger.error(str(ex))
    pass

'''
this function is for mouse emulation movements
'''
def pointer_handler():
    global ui2
    global xsession
    global factor
    xsession = False
    ui2 = None
    global xFactor
    global yFactor
    xFactor = yFactor = 0

    cap = {
        e.EV_KEY : [e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE],
        e.EV_ABS : [
            (e.ABS_X, AbsInfo(value=0, min=0, max=255,fuzz=0, flat=0, resolution=0)) ,
            (e.ABS_Y, AbsInfo(0, 0, 255, 0, 0, 0)) ,
            (e.ABS_MT_POSITION_X, (0, 128, 255, 0))
        ]
    }

    #capture current mouse coordinates. TODO If user uses a real mouse/touchpad input could confuses
    x = 20
    y = 20
    try:
        ui2 = UInput(cap, name='virtual-mouse', version=0x3)
        #it's unknown but needs 2 times to work :S
        ui2 = UInput(cap, name='virtual-mouse', version=0x3)
    except:
        logger.warning("no uinput was defined (for MOUSE virtual device)")
        pass

    #just to avoid init effect of cursor, joystick.py puts the cursor
    #ui2.write(e.EV_ABS, e.ABS_X, 0)
    #ui2.write(e.EV_ABS, e.ABS_Y, HEIGHT)
    #ui2.syn()

    while True:
        #logger.debug("%s %s" % (xFactor,yFactor))
        if x+xFactor<WIDTH and x+xFactor >=0:
            x=x+xFactor
        if y+yFactor<HEIGHT and y+yFactor >=0:
            y=y+yFactor
        if ui2:
            ui2.write(e.EV_ABS, e.ABS_X, x)
            ui2.write(e.EV_ABS, e.ABS_Y, HEIGHT-y)
            ui2.syn()

        #check if xsession
        response = str(subprocess.check_output("echo $TERM", shell=True))
        if "linux" in response:
            xsession = False
            factor = 5
        else: #TODO change it!
            xsession = True
            factor = 10
        if xsession:
            try:
                #using alternative one
                command = "xdotool mousemove %s %s" % (x,HEIGHT-y)
                process = subprocess.Popen(command.split(" "))
                #response = process.stdout.strip()
                #logger.debug("%s %s" % (x,y))
            except Exception as ex:
                #logger.error("fail pyautogui %s" % str(ex))
                pass
        #logger.debug("x: %s y: %s, xF: %s yF: %s" % (x,y,xFactor,yFactor))
        time.sleep(0.1)

logger.debug("launching mouse thread")
try:
    thread.start_new_thread(pointer_handler,())
    logger.debug("MOUSE done! launching process loop...")
except Exception as ex:
    logger.error(str(ex))

battery = 100

'''
thread function for automatic notifications like
low battery and others
'''
def notifications():

    global chargingStatus
    global batteryStatus
    global showBattery #flag to show battery

    oldAlgorithm = False
    showBattery = False

    charging = False
    batteryStatus = False
    currentShowTime = int(round(time.time() * 1000))

    while True:
        #first battery
        try:
            process = subprocess.run(BATTERY_PERCENTAGE_CMD, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            batteryStatus = int(process.stdout)
            logger.debug("%s" % str(batteryStatus))
        except:
            batteryStatus = 0
            level = 0
            pass
        try:
            process = subprocess.run(FUELGAUGE_CURRENT_CMD, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            charging = int(process.stdout) > 0
            logger.debug("charging: %s" % str(battery))
        except:
            charging = False
            pass
        if not charging and batteryStatus < 5:
            showBattery = True
            logger.debug("showing battery...")
        elif not charging and batteryStatus < 15:
            #check time loop
            if showBattery:
                showBattery = False
                currentShowTime = int(round(time.time() * 1000))
            elif currentShowTime + 20000 >= int(round(time.time() * 1000)):
                showBattery = True
                logger.debug("showing battery...")
        try:
            process = subprocess.run(BATTERY_PERCENTAGE_CMD, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            battery = int(process.stdout)
            logger.debug("battery: %s" % str(battery))
        except:
            battery = 0 #"lightning-empty-help"
            level = 0
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
            command="bin/pngview %s/resources/graphics/battery-%s.png -b 0 -l 3 -x %s -y 7 -t %s &" % (pwd,level,WIDTH-30,str(5000))
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
            command="bin/pngview %s/resources/graphics/battery-%s.png -b 0 -l 3 -x %s -y 7 -t %s &" % (pwd,level,WIDTH-30,str(5000))
        if showBattery:
            logger.debug("command... %s" % command)
            os.system(command)
            logger.debug("battery command done")
            showBattery = False
        else:
            logger.debug("not showing battery")

        time.sleep(30)

logger.debug("launching notifications thread")
try:
    thread.start_new_thread(notifications,())
    logger.debug("NOTIFICATIONS done! launching next loop...")
except Exception as ex:
    logger.error(str(ex))

'''
This function is used to control brightness and show an osd
with the current value
'''
def display_osd():

    global lightLevel
    global maxlightlevel

    global showOSDmenu

    showOSDmenu = False

    try:
        process = subprocess.Popen(BRIGHTNESS_CURRENT_CMD.split(" "))
        response = process.stdout
        currentlightlevel = int(response)

        process = subprocess.Popen(BRIGHTNESS_MAXLEVEL_CMD.split(" "))
        response = process.stdout
        maxlightlevel = int(response)

        lightLevel = 7 #will be setted in the final loop part

    except Exception as ex:
        oldAlgorithm = True
        logger.error("Could not obtain current backlight level, using old algorithm")
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(40, GPIO.OUT)
            brightness = GPIO.PWM(40, FREQ)
            brightness.start(0)
            brightness.ChangeDutyCycle(100)
            logger.debug("init done! using old algorithm to control backlight")
        except:
            logger.warning("needs pip library RPi.GPIO")
            pass

        currentlightlevel = maxlightlevel = lightLevel = 5
        pass

    while True:
        #next update lightLevel
        if currentlightlevel != lightLevel and lightLevel >= 0 and lightLevel <= maxlightlevel:
            logger.debug("changing level from %s to %s " % ( str(currentlightlevel), str(lightLevel) ))
            if oldAlgorithm:
                if lightLevel == 0:
                    brightness.ChangeDutyCycle(lightLevel)
                elif lightLevel == 1:
                    brightness.ChangeDutyCycle(20)
                elif lightLevel == 2:
                    brightness.ChangeDutyCycle(40)
                elif lightLevel == 3:
                    brightness.ChangeDutyCycle(60)
                elif lightLevel == 4:
                    brightness.ChangeDutyCycle(80)
                else:
                    brightness.ChangeDutyCycle(100)
            else:
                try:
                    command = "echo %s > %s" % (str(lightLevel),BRIGHTNESS_SETUP_CMD)
                    os.system(command)
                    currentlightlevel = lightLevel
                    logger.debug("command was %s" % command)
                except Exception as ex:
                    logger.error(str(ex))
                    pass
                if lightLevel > 0:
                    # Open template and get drawing context
                    im = Image.open('%s/resources/graphics/progress.png' % pwd ).convert('RGB')
                    draw = ImageDraw.Draw(im)

                    # Cyan-ish fill colour
                    color=(20,200,255)

                    # Draw circle at right end of progress bar
                    part = (634/maxlightlevel) * lightLevel

                    x, y, diam = part, 8, 34
                    draw.ellipse([x,y,x+diam,y+diam], fill=color)

                    # Flood-fill from extreme left of progress bar area to behind circle
                    ImageDraw.floodfill(im, xy=(14,24), value=color, thresh=40)

                    # Save result
                    im.save('/tmp/brightness-bar.png')

                    #show result
                    command="bin/pngview /tmp/brightness-bar.png -b 0 -l 2 -x 0 -y 0 -t %s &" % str(1500)
                    os.system(command)

        #last show OSD menu
        if showOSDmenu:
            logger.debug("osd command launched")
            command="bin/pngview %s/resources/graphics/logo.png -b 0 -l 5 -x 0 -y 0 -t %s &" % (os.getcwd() , str(1500))
            os.system(command)
            showOSDmenu = False


        time.sleep(0.01)

logger.debug("launching display_osd thread")
try:
    thread.start_new_thread(display_osd,())
    logger.debug("display_osd done! launching process loop...")
except Exception as ex:
    logger.error(str(ex))

'''
This function refresh list process available at this moment.
If it works fine will define the refresh time of main loop;
which has the emulator keys interpreter
'''
#should be a indepent thread
def check_process():
    global activeProcesses
    activeProcesses = []
    while True:
        for process in KEYS:
            try:
                #if isset assign in to activeProcess
                processName = process["process"]
                for proc in psutil.process_iter():
                    try:
                        # Check if process name contains the given name string.
                        if processName.lower() in proc.name().lower():
                            #found, now check list and flag like active
                            logger.debug("flag process %s" % processName)
                            found = False
                            for activeProcess in activeProcesses:
                                if processName in activeProcess["name"]:
                                    activeProcess["active"] = True
                                    found = True
                            if not found:
                                activeProcess = {}
                                activeProcess["name"] = processName
                                activeProcess["active"] = True
                                activeProcesses.append(activeProcess)
                            logger.debug("found %s running" % processName)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        for activeProcess in activeProcesses:
                            if processName in activeProcess["name"]:
                                activeProcess["active"] = False
                        logger.debug("not found %s running" % processName)
                        pass
                #check_output(["pidof",name])
                #activeProcess[name] = True
            except Exception as ex:
                logger.error("some fatal ex %s" % str(ex))
                pass
        #logger.debug("sleep 1 second...")
        time.sleep(7)


logger.debug("launching MAIN joystick.py thread")
try:
    thread.start_new_thread(check_process,())
    logger.debug("MAIN running! continue with main loop...")
except Exception as ex:
    logger.error(str(ex))

# Main event loop

ui = None
try:
    ui = uinput.UInput()
except:
    logger.warning("no uinput was defined")

while True:
    evbuf = jsdev.read(8) #wait until event happens
    logger.debug("event js: %s" % str(evbuf) )
    if evbuf:
        t, value, type, number = struct.unpack('IhBB', evbuf)

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
            device = process.stdout.strip()
            logger.debug("device is: %s" % device)
            if button_states["UP"]:
                logger.debug("bundle up detected")
                command = 'amixer set %s -- 10%%+' % device
                os.system(command)
                logger.debug("command %s" % command)
            elif button_states["DOWN"]:
                logger.debug("bundle down detected")
                command = 'amixer set %s -- 10%%-' % device
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
            showBattery = True
        elif button_states["SELECT"] and button_states["DOWN"]:
            logger.debug("bundle2 down detected")
            showOSDmenu = True
        elif button_states["SELECT"] and button_states["LEFT"]:
            lightLevel = lightLevel - 1 if lightLevel >= 1 else 0
            logger.debug("brightness - is %s" % lightLevel)
            try:
                process = subprocess.Popen(BRIGHTNESS_CURRENT_CMD.split(" "))
                response = process.stdout
                currentlightlevel = int(response)
            except Exception as ex:
                currentlightlevel = lightLevel
                logger.debug(str(ex))
                pass
        elif button_states["SELECT"] and button_states["RIGHT"]:
            lightLevel = lightLevel + 1 if lightLevel < maxlightlevel else maxlightlevel
            logger.debug("brightness + is %s" % lightLevel)
            try:
                process = subprocess.Popen(BRIGHTNESS_CURRENT_CMD.split(" "))
                response = process.stdout
                currentlightlevel = int(response)
            except Exception as ex:
                currentlightlevel = lightLevel
                logger.debug(str(ex))
                pass

        #starts dynamic emulation keys

        #input conversor
        for process in KEYS:
            name = process["process"]
            logger.debug(name)
            try:
                #if isset continue
                found = False
                for activeProcess in activeProcesses:
                    if name in activeProcess["name"]:
                        found = True
                        logger.debug("found process %s" % name)
                if found:
                    logger.debug("active process %s" % (name))
                    for key in process["keys"]:
                        type = key["type"] #e.EV_KEY
                        if key["key"] in button_states and button_states[key["key"]]: #push
                            #ui.write(e.EV_KEY, e.KEY_UP, 1) getattr(this_prize,choice)
                            for value in key["callback"]:
                                if ui:
                                    ui.write(getattr(e,type), getattr(e,value), 1)
                                elif xsession:
                                    #build key to push
                                    logger.debug("pressed: "+value)
                                    keys = value.split("_")
                                    command = ""
                                    if keys[0].upper() == 'BTN': #click
                                        if keys[1].upper() == 'LEFT':
                                            command = "xdotool mousedown 1"
                                        elif keys[1].upper() == 'RIGHT':
                                            command = "xdotool mousedown 2"
                                        elif keys[1].upper() == 'MIDDLE':
                                            command = "xdotool mousedown 3"
                                    else: #key part -> see https://gitlab.com/cunidev/gestures/-/wikis/xdotool-list-of-key-codes
                                        key = keys[1]
                                        if key == 'ESC':
                                            key = 'Escape'
                                        elif key == 'ENTER' or key == 'RETURN':
                                            key = 'Return'
                                        command = "xdotool keydown %s" % (key)
                                        logger.debug("key with command '%s'" % command)
                                    if command != "":
                                        subprocess.Popen(command.split(" "))
                        elif key["key"] in button_states and not button_states[key["key"]]: #release
                            for value in key["callback"]:
                                if ui:
                                    ui.write(getattr(e,type), getattr(e,value), 0)
                                elif xsession:
                                    #build key to push
                                    logger.debug("released: "+value)
                                    keys = value.split("_")
                                    command = ""
                                    if keys[0].upper() == 'BTN': #click
                                        if keys[1].upper() == 'LEFT':
                                            command = "xdotool mouseup 1"
                                        elif keys[1].upper() == 'RIGHT':
                                            command = "xdotool mouseup 2"
                                        elif keys[1].upper() == 'MIDDLE':
                                            command = "xdotool mouseup 3"
                                    else: #key part -> see https://gitlab.com/cunidev/gestures/-/wikis/xdotool-list-of-key-codes
                                        key = keys[1]
                                        if key == 'ESC':
                                            key = 'Escape'
                                        elif key == 'ENTER' or key == 'RETURN':
                                            key = 'Return'
                                        command = "xdotool keyup %s" % (key)
                                        logger.debug("key with command '%s'" % command)
                                    if command != "":
                                        logger.debug("release command '%s'" % command)
                                        subprocess.Popen(command.split(" "))
                                #clean (patch)
                                button_states.pop(key["key"])
                        if ui:
                            ui.syn()
                        #mouse other ui device
                        if key["key"] == "MOUSE":
                            if axis_states["x"]>0.1:
                                xFactor = int(factor*axis_states["x"])
                            elif axis_states["x"]<-0.1:
                                xFactor = int(factor*axis_states["x"])
                            else:
                                xFactor = 0
                            if axis_states["y"]>0.1:
                                yFactor = int(factor*axis_states["y"])
                            elif axis_states["y"]<-0.1:
                                yFactor = int(factor*axis_states["y"])
                            else:
                                yFactor = 0
                            #logger.debug("xF: %s, yF: %s" % (xFactor,yFactor))

            except Exception as ex:
                logger.debug("EXC: %s - %s " % (sys.exc_info(),str(ex)))
                pass
