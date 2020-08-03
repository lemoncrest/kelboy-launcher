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
pid=$(ps -aux | grep -i main.py | grep python | awk '{print $2}')

kill -9 $pid

#previews path, should be /home/pi/
cd ..
#remove old code
rm -Rf kelboy-launcher
#clone new one
git clone https://github.com/lemoncrest/kelboy-launcher
cd kelboy-launcher
chmod +x bin/*.sh
chmod +x *.sh
