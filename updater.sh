#!/bin/bash

python updater.py
mv kelboy-launcher-master /tmp/kelboy-launcher
cd ..
echo "replacing..."
rm -Rf kelboy-launcher
mv /tmp/kelboy-launcher .
echo "done!"
cd kelboy-launcher
echo "launching new revision..."
python main.py &
