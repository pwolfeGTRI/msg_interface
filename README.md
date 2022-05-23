# Skai AI Standard Message Definitions & Interface Classes

Feel free to include this as a submodule in your repo: 
```
git submodule add https://github.com/skAIVision/skai-ai-message-interface.git
```


To install in your docker container copy these lines in to install protobufs first:
```bash
ARG PROTOBUFVER=3.19.4
# install protobuf compiler and C++
RUN apt update && apt-get install -y autoconf automake libtool curl make g++ unzip && \
    cd /root/ &&\
    wget https://github.com/protocolbuffers/protobuf/releases/download/v3.19.4/protobuf-all-${PROTOBUFVER}.tar.gz && \
    tar -xzf protobuf-all-${PROTOBUFVER}.tar.gz && \
    cd protobuf-${PROTOBUFVER} && \
    ./configure && \
    make && \
    make check && \
    make install && \
    ldconfig
# install python with C++ backend for speed / data efficiency
RUN cd /root/protobuf-${PROTOBUFVER}/python && \
  python3 setup.py build --cpp_implementation && \
  python3 setup.py install --cpp_implementation 
# cleanup
RUN cd /root/ && rm protobuf-all-${PROTOBUFVER}.tar.gz && rm -rf protobuf-${PROTOBUFVER}
```

Then paste in these lines to install the skaimsginterface python package (assumes submodule folder at your top level and name unchanged)
```bash
# install skaimsginterface as a python package
COPY skai-ai-message-interface/package /root/skaimsginterface_package
RUN cd /root/skaimsginterface_package && ./install_skaimsginterface.sh
```

For how to import and use see the main of `skai-ai-message-interface/package/skaimsginterface/tcp/TcpSender.py`


## Message Definitions
See SkaiMessages.py and .proto files in protobuf folder

## TCP Interface Classes
See: 
- MultiportTcpListener.py
- TcpSender.py
- TcpSender.hpp

## TCP Message Sync
See TcpMessageSync.py

## Database Interfacing
See SkaiDatabaseInterface.py

