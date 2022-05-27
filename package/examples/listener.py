#!/usr/bin/env python3
from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import MultiportTcpListener

def example_multiport_callback_func(data, server_address):
    # store it, unpack, etc do as you wish
    msg_type, msg = SkaiMsg.unpack(data)
    print(f'got some data length {len(data)} from {server_address} msg type {msg_type}\n')


if __name__ == '__main__':
    # ports to listen to
    camgroup_idx = 0
    ports = [
        SkaimotMsg.ports[camgroup_idx],
        PoseMsg.ports[camgroup_idx],
        FeetPosMsg.ports[camgroup_idx],
        LocalTrackMsg.ports[camgroup_idx],
        GlobalTrackMsg.ports[camgroup_idx],
        ]

    # listen
    MultiportTcpListener(portlist=ports, multiport_callback_func=example_multiport_callback_func)

    # stay active until ctrl+c input
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('exiting now...')