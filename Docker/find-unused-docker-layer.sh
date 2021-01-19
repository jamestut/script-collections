#!/bin/bash
DRIVER=overlay2
DOCKERHOME=/var/lib/docker

LAYERS=`ls $DOCKERHOME/$DRIVER`
for LAYER in $LAYERS
do
  # echo $LAYER
  STATUS=`find $DOCKERHOME/image -type f -exec fgrep $LAYER {} +`
  # echo $STATUS
  if [ -z "$STATUS" ]
  then
    echo $LAYER
  fi
done
