#!/usr/bin/python3

import hashlib
import socket
import struct
import time

from skaimsginterface.skaimessages import *


class TcpSender:

    ipv4_localhost = '127.0.0.1'
    ipv6_localhost = '::1' # expands to 0:0:0:0:0:0:0:1, listen on '::' for receiving
    
    def __init__(self,
                 host_ip,
                 port,
                 retryLimit=None,
                 retryTimeoutSec=2,
                 ipv6=False, # default to ipv4
                 verbose=False) -> None:
        self.ipv6 = ipv6
        self.verbose = verbose
        self.retryLimit = retryLimit
        self.retryTimeoutSec = retryTimeoutSec
        
        # create tcp socket allowing reuse ports
        self.destination = (host_ip, port)
        if self.ipv6:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.localhost = self.ipv6_localhost
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.localhost = self.ipv4_localhost
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # try to connect with limits
        self.connect_to_destination()

    def try_to_connect(self):
        success = False
        try:
            self.sock.connect(self.destination)
            if self.verbose:
                print(f'{self.destination} connected!')
            success = True

        except ConnectionRefusedError:
            print(f'{self.destination} connection refused')

        except Exception as e:
            print(f'some other exception occurred: {e}')

        if not success:
            print(f'trying again in {self.retryTimeoutSec} seconds')
            time.sleep(self.retryTimeoutSec)

        return success

    def connect_to_destination(self):
        self.connected = False
        if self.retryLimit is None:
            while not self.connected:
                self.connected = self.try_to_connect()
        else:
            for i in range(self.retryLimit):
                self.connected = self.try_to_connect()
        
        if not self.connected:
            print('failed to connect!')

    def send(self, msg_bytes, send_failed_checksum=False):
        # calc checksum 
        clean_checksum = hashlib.md5(msg_bytes).digest()
        # if you want to send a intentionally false checksum then mutate the bytes
        if send_failed_checksum:
            # add 1 to each bytes
            checksum = b''
            for b in clean_checksum:
                checksum += bytes([b+1])
        else:
            checksum = clean_checksum
        # and append
        msg_bytes_with_checksum = msg_bytes + checksum

        msg_bytes_with_len = struct.pack('!I', len(msg_bytes_with_checksum)) + msg_bytes_with_checksum
        while True:
            try:
                self.sock.sendall(msg_bytes_with_len)
                if self.verbose:
                    print(
                        # length added in front as an unsigned int
                        f'sent { SkaiMsg.getMessageTypeName(msg_bytes)} message with length {len(msg_bytes)}'
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


    # assume first camera group only for this test
    cam_group_idx = 0

    # create senders
    verbose = True
    skaimot_sender = TcpSender('127.0.0.1', SkaimotMsg.ports[cam_group_idx], verbose=verbose)
    pose_sender = TcpSender('127.0.0.1', PoseMsg.ports[cam_group_idx], verbose=verbose)
    feetpos_sender = TcpSender('127.0.0.1',
                               FeetPosMsg.ports[cam_group_idx],
                               verbose=verbose)

    ### example message params ###
    
    # testing 2 people in frame, 5 cameras in camera group
    num_people = 2
    num_cams = 5

    # example skaimot track ids 
    # repeated across cams for testing
    trackid_list = [42, 69, 113, 1244, 333] 

    # example camera id numbers
    cam_identifier_macs = ['00:10:FA:66:42:11', '00:10:FA:66:42:21', '00:10:FA:66:42:31', '00:10:FA:66:42:41', '00:10:FA:66:42:51']
    cam_identifier_nums = SkaiMsg.convert_mac_addr_to_camera_identifier_number(cam_identifier_macs)

    # example timestamp (feel free to reuse everywhere for testing)
    ts = int(time.time() * 1e9)  # integer version of double * 1e9
    
    ### example skaimot message ###
    bbox = [0.2, 0.21, 0.4, 0.42]
    face_embed = np.arange(512).tolist()
    bbox_embed = np.arange(2048).tolist()
    # create new protobuf message and load with values
    msg = SkaimotMsg.new_msg()
    for cam_idx in range(num_cams):
        
        # add new camera frame to the message & set id + timestamp
        camframe = msg.camera_frames.add()
        camframe.camera_id = cam_identifier_nums[cam_idx]
        camframe.timestamp = ts # reuse for testing

        # add people to frame
        for person_idx in range(num_people):
            person = camframe.people_in_frame.add()
            # set person's metadata
            person.id = trackid_list[person_idx]
            SkaimotMsg.set_bbox(person, bbox)
            SkaimotMsg.set_face_embed(person, face_embed)
            # SkaimotMsg.set_bbox_embed(person, bbox_embed) # can't handle over 65535 bytes?
    skaimot_bytes = SkaimotMsg.pack(msg)

    ### example pose message ###
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
        camframe.camera_id = cam_identifier_nums[cam_idx]
        camframe.timestamp = ts # reuse for testing
        
        # add people to frame
        for person_idx in range(num_people):
            person = camframe.people_in_frame.add()
            # set person's metadata
            PoseMsg.set_keypoints(person, example_keypoints) # reuse for testing
    # pack for sending across network
    pose_bytes = PoseMsg.pack(msg) # adds message type id in front 
        

    ### example feet position message ###
    example_feetpos = [420, 69.2, 0] # xyz float meters to be reused per person

    # create new protobuf message and load with values
    msg = FeetPosMsg.new_msg()
    for cam_idx in range(num_cams):
        
        # add new camera frame to the message & set id + timestamp
        camframe = msg.camera_frames.add() 
        camframe.camera_id = cam_identifier_nums[cam_idx]
        camframe.timestamp = ts # reuse for testing
        
        # add people to frame
        for person_idx in range(num_people):
            person = camframe.people_in_frame.add()
            # set person's metadata
            person.id = trackid_list[person_idx]
            FeetPosMsg.set_feet_pos(person, example_feetpos) # reuse same foot_pos for testing
    
    # pack for sending across network
    feet_bytes = FeetPosMsg.pack(msg) # add message type id in front 


    # send 3 frames as a test with slight random offsets
    # wait 4 seconds before sending
    # time.sleep(4)
    # for i in range(3):
    #     skaimot_sender.send(skaimot_bytes)
    #     time.sleep(0.0524)
    #     pose_sender.send(pose_bytes)
    #     time.sleep(0.0112)
    #     feetpos_sender.send(feet_bytes)
    #     time.sleep(0.25)  # simulate ~4 fps


    skaimot_sender.send(skaimot_bytes)
    # pose_sender.send(pose_bytes)
    # feetpos_sender.send(feet_bytes)
    print('end')
