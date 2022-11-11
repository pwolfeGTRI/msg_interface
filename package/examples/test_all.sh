#!/bin/bash
UDP_OR_TCP=${1:-tcp}
CAMGROUP=$2
EXAMPLEOUT=$3

if [ -z "$UDP_OR_TCP" ] ; then
    echo ""
    echo "first arg UDP_OR_TCP is required. choices:"
    echo "    tcp"
    echo "    udp"
    echo ""
    exit
fi
if [ ! -z "$CAMGROUP" ] ; then
    CAMGROUPCHANGE="--camgroup $CAMGROUP"
else
    CAMGROUPCHANGE=""
fi 
if [ ! -z "$EXAMPLEOUT" ] ; then 
    EXAMPLEOUTCHANGE="--exampleout"
else
    EXAMPLEOUTCHANGE=""
fi

ARGS="$UDP_OR_TCP $EXAMPLEOUT $CAMGROUPCHANGE"

./test_action.py $ARGS
./test_feetpos.py $ARGS
./test_localtrack.py $ARGS
./test_pose.py $ARGS
./test_skaimot.py $ARGS
./test_tracksindealership.py $ARGS
./test_interactionindealership.py $ARGS
./test_vehicle.py $ARGS
./test_vehicle_spotmonitor.py $ARGS
./test_skaigooey.py $ARGS