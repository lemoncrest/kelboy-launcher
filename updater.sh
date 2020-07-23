#!/bin/bash

python updater.py
#mv /tmp/kelboy-launcher-master /tmp/kelboy-launcher
cd ..
echo "replacing..."
mv /tmp/kelboy-launcher kelboy-launcher
echo "done!"
cd kelboy-launcher
echo "launching new revision..."
python main.py &
