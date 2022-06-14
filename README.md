# Skai AI Standard Message Definitions & Interface Classes

Feel free to include this as a submodule in your repo: 
```
git submodule add https://github.com/skAIVision/skai-ai-message-interface.git
```


To install in your docker container copy these lines in to install protobufs first:
```bash
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
    ldconfig && \
    cd python && \
    python3 setup.py build --cpp_implementation && \
    python3 setup.py install --cpp_implementation && \
    cd /root/ && rm protobuf-all-${PROTOBUFVER}.tar.gz && rm -rf protobuf-${PROTOBUFVER}
```

Then paste in these lines to install the skaimsginterface python package (assumes submodule folder at your top level and name unchanged)
```bash
# install skaimsginterface as a python package
COPY skai-ai-message-interface/package /root/skaimsginterface_package
RUN cd /root/skaimsginterface_package && ./install_skaimsginterface.sh
```

## Examples
See `package/examples` folder

First run ./listener.py to listen for the example tcp messages
Then run which ever example you want. Feel free to copy example to use in your code.

## Message Definitions

See `package/skaiproto` folder and `skaimsginterface/skaimessages/SkaiMessages.py` and examples on how to use them in `packages/examples`


## UDP/TCP Interface Classes
See: 
- MultiportTcpListener.py
- TcpSender.py
- MultiportUdpListener.py
- UdpSender.py

For message time synchronization example see local track handler repo, metadata_sync.py MetadataTimeSynchronizer class

## Database Interfacing
See SkaiDatabaseInterface.py

- [ ] action example update
- [ ] local track example update with action
- [ ] action enum populate
- [ ] work on global track later
