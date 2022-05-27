#!/usr/bin/python3
import time
import numpy as np

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import TcpSender

def create_example_posemsg(num_people=2, num_cams=5):
    camera_mac = '00:10:FA:66:42:11'
    camera_id = SkaiMsg.convert_mac_addr_to_camera_identifier_number(camera_mac)
    timestamp = int(time.time() * 1e9)  # integer version of double * 1e9

    # keypoint x y coordinates scaled between 0 and 1 for width and height
    example_keypoints = [
        [0.01, 0.01], [0.02, 0.02], [0.03, 0.03], [0.04, 0.04], [0.05, 0.05], [0.06, 0.06],
        [0.07, 0.07], [0.08, 0.08], [0.09, 0.09], [0.10, 0.10], [0.11, 0.11], [0.12, 0.12],
        [0.13, 0.13], [0.14, 0.14], [0.15, 0.15], [0.16, 0.16], [0.17, 0.17], [0.18, 0.18]
    ]
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
            PoseMsg.set_keypoints(person, example_keypoints) # reuse for testing
    return msg


if __name__=='__main__':
    msg = create_example_posemsg()
    msg_bytes = PoseMsg.pack(msg, verbose=True)
    cam_group_idx = 0
    sender = TcpSender('127.0.0.1', PoseMsg.ports[cam_group_idx], verbose=True)
    sender.send(msg_bytes)
