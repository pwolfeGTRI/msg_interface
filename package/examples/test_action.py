#!/usr/bin/python3
import time
import numpy as np

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import TcpSender

def create_example_actionmsg(num_actions=2, num_cams=5):
    trackid = 69
    camera_mac = '00:10:FA:66:42:11'
    camera_id = SkaiMsg.convert_mac_addr_to_camera_identifier_number(camera_mac)
    timestamp = int(time.time() * 1e9)  # integer version of double * 1e9

    example_action = 'People Interacting???'
    # create new protobuf message and load with values
    msg = ActionMsg.new_msg()
    for cam_idx in range(num_cams):
        
        # add new camera frame to the message & set id + timestamp
        camframe = msg.camera_frames.add() 
        camframe.camera_id = camera_id
        camframe.timestamp = timestamp
        
        # add people to frame TODO fill this out later
        # example_actions_in_frame = [example_action for x in range(num_actions)]
        # camframe.actions_in_frame.extend(example_actions_in_frame)

    return msg


if __name__=='__main__':
    msg = create_example_actionmsg()
    # print(msg)
    msg_bytes = ActionMsg.pack(msg, verbose=True)
    cam_group_idx = 0
    sender = TcpSender('127.0.0.1', ActionMsg.ports[cam_group_idx], verbose=True)
    sender.send(msg_bytes)
