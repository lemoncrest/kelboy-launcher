#!/bin/bash

cd /tmp
#git clone https://github.com/lemoncrest/Kelboy2.X_Drivers kernels

cd kernels

printed=1
#array
declare -a array=()

keep='Kelboy'
for dir in */ ; do
	if [[ ${dir:0:5} == ${keep:0:5} ]] ; then
		#echo "$printed: $dir"
		array[$((printed-1))]=${dir::-1}
		printed=$((printed+1))
	#else
		#printed=0
		#keep=$dir
		#echo "discarting $dir"
	fi
done
if [[ ${#array[@]} -gt 0 ]] ; then
	j=1
	echo "choose which kernel do you want to install: "
	for i in "${array[@]}"
	do
		echo "$j) $i"
	done
	
else
	echo "No kernels detected"
fi
