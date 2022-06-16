#!/usr/bin/python3
import time
import numpy as np
import os
from argparse import ArgumentParser

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import TcpSender
from skaimsginterface.udp import UdpSender

def create_example_posemsg(num_people=2, num_cams=5):
    camera_mac = '00:10:FA:66:42:11'
    camera_id = SkaiMsg.convert_mac_addr_to_camera_identifier_number(camera_mac)
    timestamp = int(time.time() * 1e9)  # integer version of double * 1e9

    # keypoint x y coordinates scaled between 0 and 1 for width and height
    example_keypoints = [
        [0.01, 0.01], [0.02, 0.02], [0.03, 0.03], [0.04, 0.04], [0.05, 0.05], [0.06, 0.06],
        [0.07, 0.07], [0.08, 0.08], [0.09, 0.09], [0.10, 0.10], [0.11, 0.11], [0.12, 0.12],
        [0.13, 0.13], [0.14, 0.14], [0.15, 0.15], [0.16, 0.16], [0.17, 0.17], [0.18, 0.18],
        [0.19, 0.19], [0.20, 0.20], [0.21, 0.21], [0.22, 0.22], [0.23, 0.23], [0.24, 0.24],
        [0.25, 0.25], [0.26, 0.26], [0.27, 0.27], [0.28, 0.28], [0.29, 0.29], [0.30, 0.30],
        [0.31, 0.31], [0.32, 0.32], # [,] This one is empty
    ]
    
    # 3d orientation vector (should be unit vector but doesn't matter for testing)
    example_orientation = [1.3, 4.5, 7.8]

    # create new protobuf message and load with values
    msg = PoseMsg.new_msg()
    for cam_idx in range(num_cams):

        # add new camera frame to the message & set id + timestamp
        camframe = msg.camera_frames.add()
        camframe.camera_id = camera_id
        camframe.timestamp = timestamp
        
        # add people to frame
        for person_idx in range(num_people):
            person = camframe.people_in_frame.add()
            # set person's metadata
            PoseMsg.set_keypoints(person, example_keypoints, timestamp) # reuse for testing
            PoseMsg.set_orientation(person, example_orientation, timestamp)
    return msg


if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument('udp_or_tcp', type=str, help='', choices=('tcp', 'udp'))
    args = parser.parse_args()
    
    msg = create_example_posemsg()
       
    # write example message to file for viewing
    filename = 'example_msg_prints/pose.txt'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        f.write(f'{msg}')

    msg_bytes = PoseMsg.pack(msg, verbose=True)
    cam_group_idx = 0
    if args.udp_or_tcp == 'udp':
        sender = UdpSender('127.0.0.1', SkaimotMsg.ports[cam_group_idx], verbose=True)
    else:    
        sender = TcpSender('127.0.0.1', PoseMsg.ports[cam_group_idx], verbose=True)
    sender.send(msg_bytes)

