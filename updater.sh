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

cd ..
rm -Rf kelboy-launcher
git clone https://github.com/lemoncrest/kelboy-launcher
cd kelboy-launcher
chmod +x updater.sh
python3 main.py
