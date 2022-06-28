#!/usr/bin/python3
import time
from pathlib import Path
from argparse import ArgumentParser

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import TcpSender
from skaimsginterface.udp import UdpSender

from test_skaimot import create_example_skaimotmsg

def create_example_actionmsg(num_people=2, num_cams=5, num_actions=1):

    skaimotmsg = create_example_skaimotmsg(num_people=num_people, num_cams=num_cams)

    camera_mac = '00:10:FA:66:42:11'
    camera_id = SkaiMsg.convert_mac_addr_to_camera_identifier_number(camera_mac)
    timestamp = int(time.time() * 1e9)  # integer version of double * 1e9

    # create new protobuf message and load with values
    msg = ActionMsg.new_msg()
    for cam_idx in range(num_cams):

        skaimotframe = skaimotmsg.camera_frames[cam_idx]
        
        # add new camera frame to the message & set id + timestamp
        camframe = msg.camera_frames.add() 
        camframe.camera_id = camera_id
        camframe.timestamp = timestamp
        
        # TODO fill this out later
        for action_idx in range(num_actions):
            action = camframe.actions_in_frame.add()
            action.action = SkaiMsg.ACTION.TRIPPING
            
            # set to same as a skaimot person for now
            # do association by iou maybe later
            # action.location.CopyFrom(skaimotframe.people_in_frame[0].box)

            # associatedBox = action.associated_boxes.add()

            
        # example_actions_in_frame = [example_action for x in range(num_actions)]
        # camframe.actions_in_frame.extend(example_actions_in_frame)

    return msg



if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument('udp_or_tcp', type=str, help='', choices=('tcp', 'udp'))
    parser.add_argument('--exampleout', help='dump an example message text file under a folder example_msg_prints', nargs='?', type=bool, const=True, default=False)
    parser.add_argument('--camgroup', help='camera group number (default 0)', nargs='?', type=int, default=0)
    args = parser.parse_args()

    msg = create_example_actionmsg()
    
    # write example message to file for viewing
    if args.exampleout:
        filename = 'example_msg_prints/action.txt'
        print(f'wrote example message to {filename}')
        p = Path(filename)
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_text(f'{msg}') 
    
    msg_bytes = ActionMsg.pack(msg, verbose=True)
    cam_group_idx = args.camgroup
    if args.udp_or_tcp == 'udp':
        sender = UdpSender('127.0.0.1', SkaimotMsg.ports[cam_group_idx], verbose=True)
    else:    
        sender = TcpSender('127.0.0.1', ActionMsg.ports[cam_group_idx], verbose=True)
    sender.send(msg_bytes)
