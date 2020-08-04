#!/bin/bash
echo "welcome to kelboy-launcher"
killall -9 pngview

cd bin
./battery.sh &
cd ..
#exitCode=$(python3 main.py)
exitCode=$(python3 main.py 2>&1 )
status=$?
#echo "exit code is $status"
if [ $status>0 ]
then
  if [ $status == 10 ]
  then
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
