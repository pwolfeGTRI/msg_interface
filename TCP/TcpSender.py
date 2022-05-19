#!/usr/bin/python3

import socket
import struct

import time
from SkaiMessages import *


class TcpSender:

    def __init__(self,
                 host_ip,
                 port,
                 retryLimit=15,
                 retryTimeoutSec=2,
                 verbose=False) -> None:
        self.verbose = verbose
        self.retryLimit = retryLimit
        self.retryTimeoutSec = retryTimeoutSec

        # create socket
        self.destination = (host_ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # try to connect with limits
        self.connect_to_destination()

    def connect_to_destination(self):
        for i in range(self.retryLimit):
            try:
                self.sock.connect(self.destination)
                print(f'{self.destination} connected!')
                break

            except ConnectionRefusedError:
                print(f'{self.destination} connection refused')

            except Exception as e:
                print(f'some other exception occurred: {e}')

            print(f'trying again in {self.retryTimeoutSec} seconds')
            time.sleep(self.retryTimeoutSec)

    def send(self, msg_bytes):
        msg_bytes_with_len = struct.pack('!I', len(msg_bytes)) + msg_bytes
        while True:
            try:
                self.sock.sendall(msg_bytes_with_len)
                if self.verbose:
                    print(
                        # length added in front as an unsigned int
                        f'sent { SkaiMsg.getMessageTypeName(msg_bytes)} mesage with length {len(msg_bytes)}'
                    )
                    # print(f'\tfull message: {msg_bytes_with_len}')
                break

            except BrokenPipeError:
                print(f'{self.destination} connection broken!')

                # close, recreate, and try to reconnect
                self.sock.close()
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connect_to_destination()

            except Exception as e:
                print(f'some other Exception {e} occurred. exiting...')
                exit(1)


if __name__ == '__main__':

    # create senders
    verbose = True
    skaimot_sender = TcpSender('127.0.0.1', SkaimotMsg.port, verbose=verbose)
    pose_sender = TcpSender('127.0.0.1', PoseMsg.port, verbose=verbose)
    feetpos_sender = TcpSender('127.0.0.1',
                               FeetPositionMsg.port,
                               verbose=verbose)

    # create skaimot test message
    ts = time.time()  # use double not float
    trackid_list = [42, 69]
    bbox_list = [[0.2, 0.21, 0.4, 0.42], [0.2, 0.21, 0.4, 0.42]]
    num_faces = 2
    face_embed_list = []
    for i in range(num_faces):
        face_embed_list.append(np.arange(512).tolist())
    skaimot_bytes = SkaimotMsg.pack(ts, trackid_list, bbox_list,
                                    face_embed_list)

    # create pose test message
    num_people = 2
    person_example = [
        1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11,
        12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18
    ]
    pose_list = [person_example for x in range(num_people)]
    pose_bytes = PoseMsg.pack(ts, pose_list)

    # create feet pos test message
    feetpos_list = [[420, 69.2, 0], [69, 69, 0]]
    feet_bytes = FeetPositionMsg.pack(ts, feetpos_list)

    # send 3 frames as a test with slight random offsets
    # wait 4 seconds before sending
    time.sleep(4)
    for i in range(3):
        skaimot_sender.send(skaimot_bytes)
        time.sleep(0.0524)
        pose_sender.send(pose_bytes)
        time.sleep(0.0112)
        feetpos_sender.send(feet_bytes)
        time.sleep(0.25)  # simulate ~4 fps

    print('end')
