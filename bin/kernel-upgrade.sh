#!/bin/bash

cd /tmp
git clone https://github.com/lemoncrest/Kelboy2.X_Drivers kernels

cd kernels

printed=0
keep=''
for dir in */ ; do
	if [[ ${} == ${} ]] ; then
		if (( !printed)) ; then
			echo "$keep"
			printed=1
		fi
	else
		printed=0
		keep=$dir
	fi
done


