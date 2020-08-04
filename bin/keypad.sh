#!/bin/bash
while true; do
	result=jstest --event /dev/input/js0 | grep -m 1 "type 1, time .*, number .*, value 1"
  echo $result
  sleep 0.01
done
