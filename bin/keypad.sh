#!/bin/bash

function joy(){
  jstest --event /dev/input/js0 1> joystick.log
}

while true; do
  joy
  sleep 0.05
  PID=$(ps -e | grep jstest | cut -c 1-5) >/dev/null 2>&1
  sudo kill -9 $PID 1>/dev/null
  MATCH=$(grep -w "${GRAB}" joystick.log | cut -c 32-) >/dev/null 2>&1
  case $MATCH in
    "number 11, value 1" ) echo "UP" ;;
    "number 11, value 0" ) echo "UP released" ;;
    "number 10, value 1" ) echo "DOWN" ;;
    "number 10, value 0" ) echo "DOWN released" ;;
    "number 9, value 1" ) echo "LEFT" ;;
    "number 9, value 0" ) echo "LEFT released" ;;
    "number 8, value 1" ) echo "RIGHT" ;;
    "number 8, value 0" ) echo "RIGHT released" ;;
  esac
done
rm joystick.log
