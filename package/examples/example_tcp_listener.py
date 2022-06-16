#!/usr/bin/env python3
from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import MultiportTcpListener

def example_multiport_callback_func(data, server_address):
    # store it, unpack, etc do as you wish
    msg_type, msg = SkaiMsg.unpack(data)
    print(f'got some data length {len(data)} from {server_address} msg type {msg_type}\n')
    # unpack_and_print_cam_id_and_timestamp_per_frame(data)
    print(msg)
    # print(msg.camera_frames[0].people_in_frame)
    # print(msg.camera_frames[0].people_in_frame[0].orientation)

def unpack_and_print_cam_id_and_timestamp_per_frame(msg_bytes):
    # unpack message
    msg_type, msg = SkaiMsg.unpack(msg_bytes)
    print(f'got msg type {msg_type}, data: {msg}')
    for frame_data in msg.camera_frames:
        # print camera id and timestamp
        print(f'cam id: {frame_data.camera_id}, timestamp: {frame_data.timestamp}')
    

if __name__ == '__main__':
    # ports to listen to
    camgroup_idx = 0
    ports = [
        SkaimotMsg.ports[camgroup_idx],
        PoseMsg.ports[camgroup_idx],
        FeetPosMsg.ports[camgroup_idx],
        LocalTrackMsg.ports[camgroup_idx],
        GlobalTrackMsg.ports[camgroup_idx],
        ActionMsg.ports[camgroup_idx]
        ]

    # listen
    MultiportTcpListener(portlist=ports, multiport_callback_func=example_multiport_callback_func)

    # stay active until ctrl+c input
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('exiting now...')