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

    # create test message data
    ts = time.time() # use double not float
    trackid_list = [42, 69]
    bbox_list = [[0.2, 0.21, 0.4, 0.42], [0.2, 0.21, 0.4, 0.42]]
    num_faces = 2
    face_embed_list = []
    for i in range(num_faces):
        face_embed_list.append(np.arange(512).tolist())
     
    msg_bytes = SkaimotMsg.pack(ts, trackid_list, bbox_list, face_embed_list)

    sender = TcpSender('127.0.0.1', 6943)
    sender.send(msg_bytes)