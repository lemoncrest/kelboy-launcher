#!/bin/bash
sleep 1
killall -9 pngview

status=$(cat /sys/class/power_supply/max1726x_battery/capacity)
level="0"
if [ $status>0 ]
then
  if [ $status > 25 ]
  then
    level="25"
    if [ $status > 50 ]
    then
      level="50"
      if [ $status > 75 ]
      then
        level="75"
        if [ $status > 95 ]
        then
          level="100"
        fi
      fi
    fi
  fi
fi
command="./pngview /home/pi/kelboy-launcher/resources/graphics/battery-$level.png -b 0 -l 300003 -x 300 -y 5 &"
echo "executting: $command"
$command
#now wait for refresh
#pid=$(ps -aux | grep -i pngview | awk '{print $2}')
#command2="kill -9 $pid"
sleep 9
./battery.sh &

$command
echo "done!"
