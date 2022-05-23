#!/bin/bash

# first build protobufs
./build_protobuf_msgs.sh

# then install the skaimsginterface package
# python3 setup.py install
pip3 install .