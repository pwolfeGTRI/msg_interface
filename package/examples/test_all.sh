#!/bin/bash
UDP_OR_TCP=$1
EXAMPLEOUT=$2
CAMGROUPCHANGE=$3

if [ -z "$UDP_OR_TCP" ] ; then
    echo ""
    echo "first arg UDP_OR_TCP is required. choices:"
    echo "    tcp"
    echo "    udp"
    echo ""
    exit
fi

./test_action.py $UDP_OR_TCP $EXAMPLEOUT $CAMGROUPCHANGE
./test_feetpos.py $UDP_OR_TCP $EXAMPLEOUT $CAMGROUPCHANGE
./test_localtrack.py $UDP_OR_TCP $EXAMPLEOUT $CAMGROUPCHANGE
./test_pose.py $UDP_OR_TCP $EXAMPLEOUT $CAMGROUPCHANGE
./test_skaimot.py $UDP_OR_TCP $EXAMPLEOUT $CAMGROUPCHANGE
