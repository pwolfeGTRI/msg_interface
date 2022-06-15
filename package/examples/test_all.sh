#!/bin/bash
UDP_OR_TCP=$1

if [ -z "$UDP_OR_TCP" ] ; then
    echo "first arg UDP_OR_TCP is required"
    echo "choices:"
    echo "  tcp"
    echo "  udp"
fi

./test_action.py $UDP_OR_TCP
./test_feetpos.py $UDP_OR_TCP
./test_localtrack.py $UDP_OR_TCP
./test_pose.py $UDP_OR_TCP
./test_skaimot.py $UDP_OR_TCP