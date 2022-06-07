#!/bin/bash

# set variables for docker compose
BASENAME=skaimsginterface
PARENTDIR=`pwd | awk -F'/' '{print $(NF-1)}'`
PROJECTNAME=${BASENAME}_${PARENTDIR}
IMAGENAME=${BASENAME}_img_${PARENTDIR}
CONTAINERNAME=${BASENAME}_instance_${PARENTDIR}

echo BASENAME=$BASENAME > .env
echo PARENTDIR=$PARENTDIR >> .env
echo PROJECTNAME=$PROJECTNAME >> .env
echo IMAGENAME=$IMAGENAME >> .env
echo CONTAINERNAME=$CONTAINERNAME >> .env

# remove
docker-compose -p $PROJECTNAME down -t 0

# build
docker-compose build

# launch
docker-compose -p $PROJECTNAME up --detach
