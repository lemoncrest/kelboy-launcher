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
  up="0"
  down="0"
  left="0"
  right="0"
  case $MATCH in
    "Event: type 129, time 2584730, number 11, value 1" ) up="1" ;;
    "Event: type 129, time 2584730, number 11, value 0" ) up="0" ;;
    "Event: type 129, time 2584730, number 10, value 1" ) down="1" ;;
    "Event: type 129, time 2584730, number 10, value 0" ) down="0" ;;
    "Event: type 129, time 2584730, number 9, value 1" ) left="1" ;;
    "Event: type 129, time 2584730, number 9, value 0" ) left="0" ;;
    "Event: type 129, time 2584730, number 8, value 1" ) right="1" ;;
    "Event: type 129, time 2584730, number 8, value 0" ) right="0" ;;
  esac
  echo -n "$up $down $left $right"
done
rm joystick.log
