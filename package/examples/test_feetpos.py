#!/usr/bin/python3
import time
import os

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import TcpSender

def create_example_feetposmsg(num_people=2, num_cams=5):
    trackid = 69
    camera_mac = '00:10:FA:66:42:11'
    camera_id = SkaiMsg.convert_mac_addr_to_camera_identifier_number(camera_mac)
    timestamp = int(time.time() * 1e9)  # integer version of double * 1e9

    example_feetpos = [420, 69.2, 0] # xyz float meters to be reused per person
    # create new protobuf message and load with values
    msg = FeetPosMsg.new_msg()
    for cam_idx in range(num_cams):
        
        # add new camera frame to the message & set id + timestamp
        camframe = msg.camera_frames.add() 
        camframe.camera_id = camera_id
        camframe.timestamp = timestamp
        
        # add people to frame
        for person_idx in range(num_people):
            person = camframe.people_in_frame.add()
            # set person's metadata
            person.id = trackid
            FeetPosMsg.set_feet_pos(person, example_feetpos) # reuse same foot_pos for testing    

    return msg


if __name__=='__main__':
    msg = create_example_feetposmsg()

    # write example message to file for viewing
    filename = 'example_msg_prints/feetpos.txt'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        f.write(f'{msg}')

    msg_bytes = FeetPosMsg.pack(msg, verbose=True)
    cam_group_idx = 0
    sender = TcpSender('127.0.0.1', FeetPosMsg.ports[cam_group_idx], verbose=True)
    sender.send(msg_bytes)

