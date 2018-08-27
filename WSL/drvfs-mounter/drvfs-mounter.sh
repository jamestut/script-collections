#!/bin/bash

# this script should be run as root, ideally in .bashrc

# a file that contains list of Windows volumes to mount
if [ -z $1 ]
then
	VOLFN=~/.volumes.txt
else
	VOLFN=$1
fi

# iterate thru given volume list file
VOLS=`cat $VOLFN`
MOUNTEDVOLS=`mount`
while read -r VOL
do
	NOMOUNT=
	VOLPARAM=`echo $VOL | sed 's/;/ /g'`
	VOLPARAM=($VOLPARAM)
	WINVOL=${VOLPARAM[0]}
	REQMNT=${VOLPARAM[1]}
	# check if target mountpoint is already mounted
	while read -r MOUNTEDVOLPARAM
	do
		MOUNTEDVOLPARAM=($MOUNTEDVOLPARAM)
		MOUNTPOINT=${MOUNTEDVOLPARAM[2]}
		if [ $REQMNT = $MOUNTPOINT ]
		then
			NOMOUNT=1
		fi
	done <<< "$MOUNTEDVOLS"
	# do the actual mounting
	if [ -z $NOMOUNT ]
	then
		# check folder exists
		if [ ! -d $REQMNT ]
		then
			mkdir $REQMNT
		fi
		# actually mounts
		echo mounting "$WINVOL" to $REQMNT
		mount -t drvfs "$WINVOL" $REQMNT
	fi
done <<< "$VOLS"
exit 0
