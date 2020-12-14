#!/bin/bash

cd /tmp
git clone https://github.com/lemoncrest/Kelboy2.X_Drivers kernels

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
		j=$((j+1))
	done
	while true ; do
		read -p "?)" option
		if (( option >= 1 && option <= "${#array[@]}" )); then
			echo "selected: ${array[($option-1)]}"
			cd ${array[($option-1)]}
			cd boot
			#rsync patch
			sudo rsync -auvh etc/ /etc/
			sudo rsync -auvh lib/ /lib/
			sudo rsync -auvh usr/ /usr/
			sudo rsync -auvh boot/ /boot/
			#now edit config.txt and put new kernel
			kernel=''
			for file in *.*; do
				if [[ ${file:0:6} == 'Kernel' ]]; then
					kernel=$file
				fi
			done
			echo "kernel is: $kernel"
			#sudo sed "s/^kernel=/#&/" /boot/config.txt > /tmp/config.txt
			sudo sed "s/^kernel=/kernel=$kernel/" /boot/config.txt > /tmp/config.txt
			#linenumber=$(sed -n -e '/^kernel=/=' /boot/config.txt)

			echo "done, rebooting..."
			sudo reboot
			break
		else
			echo "wrong option, try again :'("
		fi
	done
else
	echo "No kernels detected"
fi
