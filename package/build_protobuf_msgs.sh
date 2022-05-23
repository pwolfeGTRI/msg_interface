#!/bin/bash

SRC_DIR=protobuf/
PYTHON_DST_DIR=skaimsginterface/skaimessages/generated_python
CPP_DST_DIR=skaimsginterface/skaimessages/generated_cpp

echo ""
echo "cleaning..."
rm -rf $PYTHON_DST_DIR $CPP_DST_DIR

echo ""
echo "building protobuf messages..."
mkdir -p $PYTHON_DST_DIR $CPP_DST_DIR
protoc -I=$SRC_DIR --cpp_out=$CPP_DST_DIR $SRC_DIR/*.proto
protoc -I=$SRC_DIR --python_out=$PYTHON_DST_DIR $SRC_DIR/*.proto

echo "copying generated python __init__.py into destination..."
cp $SRC_DIR/generatedpy__init__.py $PYTHON_DST_DIR/__init__.py

echo "done"
echo ""