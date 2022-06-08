FROM pwolfe854/gst_ds_env:x86_64_nogpu

RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub && \
  apt update && apt install -y graphviz curl

# setup non root user nvidia (password nvidia). may need to run things some things with root still. (like pose)
RUN apt install -y sudo && \
  useradd -m nvidia && echo "nvidia:nvidia" | chpasswd && adduser nvidia sudo

# google protobufs installation for use with C++ and python 3.5 - 3.7
ARG PROTOBUFVER=3.19.4
# install protobuf compiler and C++
RUN apt update && apt-get install -y autoconf automake libtool curl make g++ unzip && \
    cd /root/ &&\
    wget https://github.com/protocolbuffers/protobuf/releases/download/v3.19.4/protobuf-all-${PROTOBUFVER}.tar.gz && \
    tar -xzf protobuf-all-${PROTOBUFVER}.tar.gz && \
    cd protobuf-${PROTOBUFVER} && \
    ./configure && \
    make && \
    make install && \
    ldconfig
# install python with C++ backend for speed / data efficiency
RUN cd /root/protobuf-${PROTOBUFVER}/python && \
  python3 setup.py build --cpp_implementation && \
  python3 setup.py install --cpp_implementation 
# cleanup
RUN cd /root/ && rm protobuf-all-${PROTOBUFVER}.tar.gz && rm -rf protobuf-${PROTOBUFVER}

# install skaimsginterface as a python package
COPY package /root/package
RUN cd /root/package && ./install_skaimsginterface.sh
# note this copies the same folder being mapped in this case.
# feel free to put it wherever in your docker

# working on the cpp classes now...
RUN apt-get install -y cmake