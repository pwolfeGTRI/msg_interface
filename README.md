# Skai AI Standard Message Definitions & Interface Classes

## Cloning

```bash
git clone https://github.com/skAIVision/skai-ai-message-interface.git
cd skai-ai-message-interface
./init_remotes.sh
```

## Pushing

To push changes to all remotes:
```bash
./push_all_remotes.sh
```

### AUTHENTICATION NOTE: 
- skai_remote relies on a personal auth token and access to skai enterprise github
- gtri_remote relies on being on the gtri vpn and eosl bitbucket access + ssh key

`skai-aurora` machines have the `skai_remote` auth setup already globally. 

`gtri_remote` requires additional setup if machine not on network (openconnect to gtri eosl vpn)

## Adding this as a submodule

To include this as a submodule in your repo: 
```
git submodule add https://github.com/skAIVision/skai-ai-message-interface.git
```


## adding this into your docker container 

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
See [packages/examples/README.md](package/examples/README.md)

Examples folder has many examples to get you setup:
- `test_*` examples show how to create, pack, and send messages.
- `example_listener.py` examples show how to listen, get message & message type, and get protobuf params from the data
- `replay_skaibin.py` shows how to replay skaibin files recorded by the listener

### Testing UDP
```bash
# in first terminal
./attach.sh
cd examples
./example_udp_listener.py

# in second terminal
./attach.sh
cd examples
./test_all.sh udp
```

### Testing TCP
```bash
# in first terminal
./attach.sh
cd examples
./example_tcp_listener.py

# in second terminal
./attach.sh
cd examples
./test_all.sh tcp
```

## Message Definitions

See `package/skaiproto` folder and `skaimsginterface/skaimessages/SkaiMessages.py` and examples on how to use them in `packages/examples`

## UDP/TCP Interface Classes
See: 
- MultiportTcpListener.py
- TcpSender.py
- MultiportUdpListener.py
- UdpSender.py

For message time synchronization example see local track handler repo, metadata_sync.py MetadataTimeSynchronizer class

## Creating a New Message

1. add a .proto file for your message first
  - validate with `build_protobuf_msgs.sh`
2. then go into package/skaimsginterface/skaimessages/SkaiMessages.py and do the following:
  - create a new class using SkaiMsg as a base
  - in `SkaiMsg` -> `MsgType` make a new type
  - in `SkaiMsg` -> `MsgType` -> `get_class_from_id` point to your new message class
  - update `msg_type`, `proto_msg_class`, and `ports` accordingly 
  - create any helper functions to pack your message
  - install with `install_skaimsginterface.sh --upgrade`
3. add an example
  - in `examples/listener.py` add your msg to be listened to
  - make an `examples/test_yourmsgname.py` file to show how to pack your message & send to listener. (see other examples and .proto files for reference)

## Database Interfacing
See SkaiDatabaseInterface.py

- [ ] action example update
- [ ] local track example update with action
- [ ] action enum populate
- [ ] work on global track later
