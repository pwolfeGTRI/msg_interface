#!/bin/bash

CONTAINERNAME=`cat .env | grep CONTAINERNAME | awk -F'=' '{print $NF}'`
echo "attaching to container: $CONTAINERNAME"

# launch bash session in container
docker exec -it $CONTAINERNAME /bin/bash
