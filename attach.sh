#!/bin/bash
CONTAINER_NAME=`cat .env  | grep CONTAINER_NAME | awk -F "=" '{print $2}'`

docker exec -it $CONTAINER_NAME /bin/bash