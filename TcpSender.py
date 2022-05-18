#!/usr/bin/python3

import socket
import struct


import time
from SkaiMessages import *

class TcpSender:
    def __init__(self, host_ip, port, verbose=False) -> None:
        # create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect
        self.sock.connect((host_ip, port))
        self.verbose = verbose

    def send(self, msg_bytes):
        msg_bytes_with_len = struct.pack('!I', len(msg_bytes)) + msg_bytes
        self.sock.sendall(msg_bytes_with_len)
        if self.verbose:
            print(f'sent: {msg_bytes} with length {len(msg_bytes)} in front (unsigned int)')
            print(f'\tfull message: {msg_bytes_with_len}')

if __name__=='__main__':

    # create a sender on port 6942
    sender = TcpSender('127.0.0.1', 6942)

    # send skaimot message
    ts = time.time() # use double not float
    trackid_list = [42, 69]
    bbox_list = [[0.2, 0.21, 0.4, 0.42], [0.2, 0.21, 0.4, 0.42]]
    num_faces = 2
    face_embed_list = []
    for i in range(num_faces):
        face_embed_list.append(np.arange(512).tolist())
    skaimot_bytes = SkaimotMsg.pack(ts, trackid_list, bbox_list, face_embed_list)
    sender.send(skaimot_bytes)
    time.sleep(1)

    # send pose message
    num_people = 2
    person_example=[1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13,14,14,15,15,16,16,17,17,18,18]
    pose_list = [person_example for x in range(num_people)]
    pose_bytes=PoseMsg.pack(ts, pose_list)
    sender.send(pose_bytes)
    time.sleep(1)

    # send feet pos message
    feetpos_list = [[420, 69.2, 0], [69, 69, 0]]
    feet_bytes = FeetPositionMsg.pack(ts, feetpos_list)
    sender.send(feet_bytes)
