#!/bin/bash
pid=$(ps -aux | grep -i main.py | grep python | awk '{print $2}')

kill -9 $pid

emulationstation --resolution 320 240

python3 main.py &
