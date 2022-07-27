#!/bin/bash

# first build protobufs
./build_protobuf_msgs.sh

# then install or upgrade
INSTALLED=`pip3 show skaimsginterface`
if [ -z "$INSTALLED" ] ; then 
    echo "skaimsginterface not installed yet. installing..."
    pip3 install .
else
    echo "skaimsginterface installed. upgrading..."
    pip3 install . --upgrade
fi
