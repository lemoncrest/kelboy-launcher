#!/bin/bash
pid=$(ps -aux | grep -i main.py | grep python | awk '{print $2}')

kill -9 $pid

emulationstation

python3 main.py
