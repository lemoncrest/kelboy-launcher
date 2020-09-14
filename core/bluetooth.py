import bluetooth
import time
import pexpect
import subprocess
import os
import sys
from core.settings import *
import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=logging.DEBUG)
logger = logging.getLogger(__name__)

"""
A wrapper for bluetoothctl utility and pybluez library.

In raspberry pi needs package:

sudo apt install pulseaudio-module-bluetooth

"""
class Bluetooth():

    def __init__(self):
        out = subprocess.check_output("rfkill unblock bluetooth", shell = True)
        self.launch()

    def get_devices(self):
        nearby_devices = bluetooth.discover_devices(lookup_names=True)
        logger.debug("Found {} devices.".format(len(nearby_devices)))
        devices = []
        for addr, name in nearby_devices:
            logger.debug("  {} - {}".format(addr, name))
            device = {}
            device["name"] = name
            device["address"] = addr
            devices.append(device)
        return devices

    def launch(self):
        self.child = pexpect.spawn("bluetoothctl")

    def off(self):
        time.sleep(0.5)
        self.child.sendline("power off")

    def on(self):
        time.sleep(0.5)
        self.child.sendline("power on")

    def scan_devices(self,wait=10):
        devices = []
        self.child.sendline('scan on')
        time.sleep(wait)
        self.child.sendline('scan off')
        line = self.child.readline()
        while b'scan off' not in line:
            if b'Device' in line:
                logger.debug("using line %s " % line)
                line = str(line.replace(b"\r\n", b'')).strip("b'").strip("'")
                address, name = line.split('Device ')[1].split(' ', 1)
                device = {}
                device["name"] = name
                device["address"] = address
                devices.append(device)
            line = self.child.readline()
        return devices

    def send(self, command, pause=0):
        self.process.send(f"{command}\n")
        time.sleep(pause)
        if self.process.expect(["bluetooth", pexpect.EOF]):
            raise Exception(f"failed after {command}")

    def get_output(self, *args, **kwargs):
        """Run a command in bluetoothctl prompt, return output as a list of lines."""
        self.send(*args, **kwargs)
        return self.process.before.split("\r\n")

    def get_available_devices(self):
        """Return a list of tuples of paired and discoverable devices."""
        available_devices = []
        try:
            out = self.get_output("devices")
        except Exception as e:
            logger.error(e)
        else:
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    available_devices.append(device)
        return available_devices

    def trust_device(self,address):
        self.child.sendline('agent off')
        time.sleep(0.2)
        self.child.sendline('pairable on')
        time.sleep(0.2)
        self.child.sendline('agent NoInputNoOutput')
        time.sleep(0.2)
        self.child.sendline('default-agent')
        time.sleep(0.2)
        self.connect(address)
        time.sleep(0.2)
        self.pair(address)
        time.sleep(0.5)
        self.child.sendline('trust %s' % address)

    def pair(self,address):
        self.child.sendline('pair %s' % address)

    def connect(self,address):
        self.child.sendline('connect %s' % address)

    def exit(self):
        self.child.sendline('exit')
