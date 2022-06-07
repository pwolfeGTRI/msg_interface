#!/bin/bash

PROJECTNAME=`cat .env | grep PROJECTNAME | awk -F'=' '{print $NF}'`
CONTAINERNAME=`cat .env | grep CONTAINERNAME | awk -F'=' '{print $NF}'`
echo removing container $CONTAINERNAME...

docker-compose -p $PROJECTNAME down -t 0
