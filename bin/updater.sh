#!/bin/bash

#python3 updater.py
#cd /home/pi
#echo "replacing..."
#rm -Rf kelboy-launcher
#mv /tmp/kelboy-launcher-master kelboy-launcher
#echo "done!"
#cd /home/pi/kelboy-launcher
#chmod +x updater.sh
#echo "launching new revision..."
#python3 main.py &

#!/bin/bash
#pid=$(ps -aux | grep -i main.py | grep python | awk '{print $2}')
#kill -9 $pid
#killall -9 battery.sh
#killall -9 pngview

#previews path, should be /home/pi/
#cd ..
#remove old code
#rm -Rf kelboy-launcher
#clone new one
#git clone https://github.com/lemoncrest/kelboy-launcher
#cd kelboy-launcher
sudo apt update
if [ ! -f /lib/arm-linux-gnueabihf/libpng12.so.0 ]; then
    echo "launching install dependencies..."
    sudo apt install libpng12-0 bsdtar -y
fi
#RPi.GPIO+
if ! python3 -c 'import pkgutil; exit(not pkgutil.find_loader("RPi.GPIO"))'; then
    sudo apt install python3-rpi.gpio -y
fi
#pulseaudio and pulseaudio-module-bluetooth
if [ $(dpkg-query -W -f='${Status}' pulseaudio 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
    sudo apt-get install pulseaudio pulseaudio-module-bluetooth -y
fi
#bluetooth controllers
if [ $(dpkg-query -W -f='${Status}' bluez-tools 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
    sudo apt-get install bluetooth python-dbus python-gobject bluez-tools -y
fi
if [ $(dpkg-query -W -f='${Status}' xinit 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
    sudo apt-get install xinit chromium-browser steamlink cec-utils libcec4 libp8-platform2 -y
fi
if [ $(dpkg-query -W -f='${Status}' youtube-dl 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
    sudo pip3 install youtube-dl -U
fi
if [ $(dpkg-query -W -f='${Status}' mplayer 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
    sudo apt install mplayer -y
fi
if [ $(dpkg-query -W -f='${Status}' mpv 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
    sudo apt-get install mpv -y
fi
if [ ! -f /usr/lib/libwiringPi.so ]; then
    sudo apt install wiringpi xdotool -y
fi
if [ $(dpkg-query -W -f='${Status}' python3-evdev 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
    sudo apt-get install -y python3-evdev
fi
if [ $(dpkg-query -W -f='${Status}' scummvm 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
    sudo apt install scummvm
fi

git reset --hard HEAD #temp fix to remove local changes to force update
git pull
chmod +x bin/*.sh
chmod +x *.sh

#restart launcher
./launcher.sh
