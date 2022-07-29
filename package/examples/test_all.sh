#!/bin/bash
UDP_OR_TCP=$1
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


./test_action.py $UDP_OR_TCP $EXAMPLEOUT $CAMGROUPCHANGE
./test_feetpos.py $UDP_OR_TCP $EXAMPLEOUT $CAMGROUPCHANGE
./test_localtrack.py $UDP_OR_TCP $EXAMPLEOUT $CAMGROUPCHANGE
./test_pose.py $UDP_OR_TCP $EXAMPLEOUT $CAMGROUPCHANGE
./test_skaimot.py $UDP_OR_TCP $EXAMPLEOUT $CAMGROUPCHANGE
./test_tracksindealership.py $UDP_OR_TCP $EXAMPLEOUT $CAMGROUPCHANGE
./test_interactionindealership.py $UDP_OR_TCP $EXAMPLEOUT $CAMGROUPCHANGE
