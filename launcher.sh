#!/bin/bash
echo "welcome to kelboy-launcher"
#sudo killall -9 pngview
#sudo killall python3
#rm bin/battery.old

#cd bin
#./battery.sh &
#cd ..
python3 joystick.py &
#exitCode=$(python3 main.py)
exitCode=$(python3 main.py 2>&1 )
status=$?
#echo "exit code is $status"
if [ $status>0 ]
then
  if [ $status == 10 ]
  then
    sudo killall -9 battery.sh
    sudo killall -9 pngview
    foo="`cat command`"
    $foo 2>&1 &
    wait
    ./launcher.sh
  fi
else
  echo "bye bye!"
fi
sleep 0.5
rm 0
rm command
