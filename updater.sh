#!/bin/bash

python3 updater.py
cd ..
echo "replacing..."
rm -Rf kelboy-launcher
mv /tmp/kelboy-launcher-master kelboy-launcher
echo "done!"
cd kelboy-launcher
chmod +x updater.sh
echo "launching new revision..."
python3 main.py &
