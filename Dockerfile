# FROM pwolfe854/gst_ds_env:x86_64_nogpu
FROM ubuntu:18.04

# protobuf apt prereqs
RUN apt update -y && apt install -y autoconf automake libtool curl make g++ unzip python3 python3-pip

# install protobufs 3.19.4 from binaries / include files x86_64 arch
ARG PROTOBUFVER=3.19.4
ARG ARCH=x86_64
ARG PB_REL="https://github.com/protocolbuffers/protobuf/releases"
ARG BASENAME="protoc-${PROTOBUFVER}-linux-${ARCH}"
RUN cd /root/ && \
    curl -LO $PB_REL/download/v${PROTOBUFVER}/${BASENAME}.zip && \
    unzip ${BASENAME}.zip -d ./${BASENAME} && \
    cp -R ${BASENAME}/bin/protoc /usr/local/bin/protoc && \
    cp -R ${BASENAME}/include/google /usr/local/include/ && \
    pip3 install numpy protobuf==${PROTOBUFVER} && \
    rm -rf $BASENAME ${BASENAME}.zip

# install skaimsginterface as a python package
COPY package /root/package
RUN cd /root/package && ./install_skaimsginterface.sh
