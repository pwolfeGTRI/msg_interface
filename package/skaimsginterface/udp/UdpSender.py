#!/usr/bin/python3

import socket
import struct

import time

from skaimsginterface.skaimessages import *

class UdpSender:

    def __init__(self,
                 host_ip,
                 port,
                 verbose=False) -> None:
        self.verbose = verbose

        # create udp socket allowing reuse ports
        self.destination = (host_ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def send(self, msg_bytes):
        ret = self.sock.sendto(msg_bytes[:1024], self.destination)
        print(ret)

def create_example_skaimotmsg(num_people=2, num_cams=5):    
    trackid = 69
    camera_mac = '00:10:FA:66:42:11'
    camera_id = SkaiMsg.convert_mac_addr_to_camera_identifier_number(camera_mac)
    timestamp = int(time.time() * 1e9)  # integer version of double * 1e9

    # example bounding boxes & face embeddings & bbox embedding per person
    bbox = [0.2, 0.21, 0.4, 0.42]
    face_embed = np.arange(512).tolist()
    bbox_embed = np.arange(2048).tolist()

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
    return msg

if __name__=='__main__':
    verbose = True
    cam_group_idx = 22
    skaimot_sender = UdpSender('127.0.0.1', SkaimotMsg.ports[cam_group_idx], verbose=verbose)
    msg = create_example_skaimotmsg()
    msg_bytes = SkaimotMsg.pack(msg, verbose=verbose)
    skaimot_sender.send(msg_bytes)

