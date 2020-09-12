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

if [ ! -f /lib/arm-linux-gnueabihf/libpng12.so.0 ]; then
    echo "launching install dependencies..."
    sudo apt install libpng12-0 bsdtar -y
fi
#RPi.GPIO
if ! python3 -c 'import pkgutil; exit(not pkgutil.find_loader("RPi.GPIO"))'; then
    sudo apt install python3-rpi.gpio -y
fi

git pull
chmod +x bin/*.sh
chmod +x *.sh

#restart launcher
./launcher.sh
