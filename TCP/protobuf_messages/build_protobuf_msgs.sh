#!/bin/bash

SRC_DIR=./
PYTHON_DST_DIR=./generated_msgs/python
CPP_DST_DIR=./generated_msgs/cpp

echo ""
echo "cleaning..."
rm -rf $PYTHON_DST_DIR $CPP_DST_DIR

echo ""
echo "building protobuf messages..."
mkdir -p $PYTHON_DST_DIR $CPP_DST_DIR
protoc -I=$SRC_DIR --cpp_out=$CPP_DST_DIR $SRC_DIR/*.proto
protoc -I=$SRC_DIR --python_out=$PYTHON_DST_DIR $SRC_DIR/*.proto

echo "done"
echo ""