#!/bin/bash
pid=$(ps -aux | grep -i main.py | grep python | awk '{print $2}')

kill -9 $pid

TTY=$(tty)
emulationstation
export TTY="$(TTY:8:1)"

python3 main.py &
