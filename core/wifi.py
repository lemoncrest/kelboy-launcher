import pexpect
import subprocess
import os
import time
from core.settings import *
import logging
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE),level=logging.DEBUG)
logger = logging.getLogger(__name__)

"""
A wrapper for wifi.
"""
class Wifi():

    def __init__(self):
        self.command = "iwlist wlan0 scan | awk -F ':' '/ESSID:/ {print $2;}'"

    def scan_networks(self,wait=6):
        self.child = pexpect.spawn(self.command) #f.i.
        time.sleep(wait)
        networks = []
        line = self.child.readline()
        while b'$' not in line:
            if b'""' not in line:
                logger.debug("using line %s " % line)
                line = str(line.replace(b"\r\n", b'')).strip("b'").strip("'")
                name = line.split('"')[1].split('"')[0]
                network = {}
                network["name"] = name
                networks.append(network)
            line = self.child.readline()
        return networks

    def buildWpaSupplicantAndConnect(self,ssid,pwd):
        line_0_default = 'country=ES'
        line_1_default = 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev'
        line_2_default = 'update_config=1'
        ssid_fix = ssid
        ssid_fix = ssid_fix.replace(' ', '\\ ')
        ssid_fix = ssid_fix.replace("'", '\'')
        pwd_fix = pwd
        pwd_fix = pwd_fix.replace(' ', '\\ ')
        pwd_fix = pwd_fix.replace("'", '\'')
        process = subprocess.run('wpa_passphrase ' + ssid_fix + ' ' + pwd_fix, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        output = process.stdout
        logger.debug(output)
        if 'network={' in output:
            with open("wpa_supplicant.conf", 'w') as (myfile):
                myfile.write(line_0_default + '\n')
                myfile.write(line_1_default + '\n')
                myfile.write(line_2_default + '\n')
                myfile.write(output)
        else:
            with open("wpa_supplicant.conf", 'w') as (myfile):
                myfile.write(line_0_default + '\n')
                myfile.write(line_1_default + '\n')
                myfile.write(line_2_default + '\n')
        process = subprocess.run('sudo mv wpa_supplicant.conf '+WPA_SUPPLICANT, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        output = process.stdout
        process = subprocess.run('wpa_cli -i wlan0 reconfigure', shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        output = process.stdout
        #p = subprocess.Popen('wpa_cli -i wlan0 reconfigure', stdout=subprocess.PIPE, shell=True)
        #output, err = p.communicate()
        #p.wait()
        self.is_connecting = True
