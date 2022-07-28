#!/usr/bin/python3
import time
import numpy as np
from pathlib import Path
from argparse import ArgumentParser

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import TcpSender
from skaimsginterface.udp import UdpSender

def create_example_skaimotmsg(num_people=2, num_cams=5, id=None):    
    if id is None:
        trackid = 69
    else:
        trackid = id
    camera_mac = '00:10:FA:66:42:11'
    camera_id = SkaiMsg.convert_mac_addr_to_camera_identifier_number(camera_mac)
    timestamp = int(time.time() * 1e9)  # integer version of double * 1e9

    # example bounding boxes & face embeddings & bbox embedding per person
    bbox = [0.2, 0.21, 0.4, 0.42]
    # full version
    # face_embed = np.arange(512).tolist()  
    # bbox_embed = np.arange(2048).tolist() 
    # short version for testing 
    face_embed = np.arange(5).tolist()  
    bbox_embed = np.arange(2).tolist() 

    # example tags
    tags = ['Manager IV', 'Manager 4', 'Manager the 4th', 'Manager the fourth', 'Person who manages stuff 4 times']

    # create new protobuf message and load with values
    msg = SkaimotMsg.new_msg()
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
            person.classification = SkaiMsg.CLASSIFICATION.EMPLOYEE
            SkaimotMsg.set_bbox(person, bbox)
            SkaimotMsg.set_face_embed(person, face_embed)
            SkaimotMsg.set_bbox_embed(person, bbox_embed)
            person.tags.extend(tags)
    return msg

if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument('udp_or_tcp', type=str, help='protocol to listen on', choices=('tcp', 'udp'))
    parser.add_argument('--exampleout', help='dump an example message text file under a folder example_msg_prints', nargs='?', type=bool, const=True, default=False)
    parser.add_argument('--camgroup', help='camera group number (default 0)', nargs='?', type=int, default=0)
    parser.add_argument('--ipv6', help='use ipv6 instead of ipv4 default', nargs='?', type=bool, const=True, default=False)
    args = parser.parse_args()

    msg = create_example_skaimotmsg()
    
    # write example message to file for viewing
    if args.exampleout:
        filename = 'example_msg_prints/skaimot.txt'
        print(f'wrote example message to {filename}')
        p = Path(filename)
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_text(f'{msg}')

    msg_bytes = SkaimotMsg.pack(msg, verbose=True)
    cam_group_idx = args.camgroup
    if args.ipv6:
        destination_ip = '::1' # TcpSender.ipv6_localhost
    else:
        destination_ip = TcpSender.ipv4_localhost
    if args.udp_or_tcp == 'udp':
        sender = UdpSender(destination_ip, SkaimotMsg.ports[cam_group_idx], verbose=True)
    else:    
        sender = TcpSender(destination_ip, SkaimotMsg.ports[cam_group_idx], ipv6=args.ipv6, verbose=True)
    sender.send(msg_bytes)
