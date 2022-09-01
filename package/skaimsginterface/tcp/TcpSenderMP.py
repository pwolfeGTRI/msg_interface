#!/usr/bin/python3

import hashlib
import socket
import struct
import time

from skaimsginterface.skaimessages import *
import multiprocessing as mp

class TcpSenderMP:

    ipv4_localhost = '127.0.0.1'
    ipv6_localhost = '::1' # expands to 0:0:0:0:0:0:0:1, listen on '::' for receiving
    
    def __init__(self,
                 host_ip,
                 port,
                 print_q, # required
                 retryLimit=None,
                 retryTimeoutSec=2,
                 ipv6=False, # default to ipv4
                 verbose=False) -> None:
        self.ipv6 = ipv6
        self.verbose = verbose
        self.retryLimit = retryLimit
        self.retryTimeoutSec = retryTimeoutSec

        # create stop event ,print queue, sender queue
        self.stop_event = mp.Event()
        self.print_q = print_q # mp.SimpleQueue()
        self.send_q = mp.SimpleQueue()

        # socket creation info
        self.destination = (host_ip, port)
        if self.ipv6:
            self.localhost = self.ipv6_localhost
        else:
            self.localhost = self.ipv4_localhost

        # actually create socket
        self.sock = self.create_socket(ipv6=self.ipv6)

        # try to connect with limits
        self.connect_to_destination(
            self.stop_event,
            self.print_q,
            self.sock,
            self.destination,
            self.retryLimit,
            self.retryTimeoutSec,
            self.verbose)

        # start sender process
        self.start_sender_process()

    def start_sender_process(self):
        port = destination[1]
        self.sender_proc = mp.Process(
            name=f'TcpSender_{port}',
            target=self.sender_process,
            args=(
                self.stop_event,
                self.print_q,
                self.send_q,
                self.sock,
                self.destination,
                self.retryLimit,
                self.retryTimeoutSec,
                self.verbose,
                self.ipv6
            )
        )

    @staticmethod
    def create_socket(ipv6=False):
        if ipv6:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock

    @staticmethod
    def try_to_connect(print_q, sock, destination, retryTimeoutSec, verbose):
        success = False
        try:
            sock.connect(destination)
            print_q.put(f'connected to {destination}!')
            success = True

        except ConnectionRefusedError:
            print_q.put(f'{destination} connection refused')

        except Exception as e:
            print(f'TcpSenderMP try_to_connect exception: {e}')

        if not success:
            print(f'trying to connect to {destination} again in {retryTimeoutSec} seconds')
            time.sleep(retryTimeoutSec)

        return success

    @staticmethod
    def connect_to_destination(stop_event, print_q, sock, destination, retryLimit, retryTimeoutSec, verbose):
        # attempt to connect once
        connected = False
        if retryLimit is None:
            while (not connected) and (not stop_event.is_set()):
                connected = TcpSenderMP.try_to_connect(print_q, sock, destination, retryTimeoutSec, verbose)
        else:
            for i in range(retryLimit):
                connected = TcpSenderMP.try_to_connect(print_q, sock, destination, retryTimeoutSec, verbose)
                if stop_event.is_set()
                    break
        
        if not connected:
            print_q.put('failed to connect!')
        
        # return results of attempt to connect
        return connected

    @staticmethod
    def sender_process(stop_event, print_q, send_q, sock, destination, retryLimit, retryTimeoutSec, verbose, ipv6=False):
        while not stop_event.is_set():
            
            # check if anything to send
            if not send_q.empty():
                
                # try sending until sent (handle disconnects too)
                sent = False
                while not sent:
                    # get msg bytes with checksum appended and length prepended
                    msg_bytes_with_checksum_and_length = send_q.get()

                    # attempt to send on socket
                    try:
                        sock.sendall(msg_bytes_with_checksum_and_length)
                        if verbose:
                            # length added in front as an unsigned int
                            print_q.put(
                                f'sent { SkaiMsg.getMessageTypeName(msg_bytes)} message bytes with length {len(msg_bytes_with_checksum_and_length)}'
                            )
                        sent = True

                    except BrokenPipeError:
                        print_q.put(f'{destination} connection broken! reconnecting...')

                        # close, recreate, and try to reconnect
                        sock.close()
                        sock = TcpSenderMP.create_socket(ipv6=ipv6)
                        TcpSenderMP.connect_to_destination(
                            stop_event,
                            print_q,
                            sock,
                            destination,
                            retryLimit,
                            retryTimeoutSec,
                            verbose
                        )

                    except Exception as e:
                        print_q.put(f'TcpSenderMP Exception: {e}')

                    if not sent:
                        print_q.put('msg not sent. retrying...')
           

    def send(self, msg_bytes):
        # calc checksum and append
        msg_bytes_with_checksum = msg_bytes + hashlib.md5(msg_bytes).digest()
        # calc length and prepend
        msg_bytes_with_checksum_and_length = struct.pack('!I', len(msg_bytes_with_checksum)) + msg_bytes_with_checksum
        # add to send queue to be sent
        self.send_q.put(msg_bytes_with_checksum_and_length)
        
if __name__ == '__main__':
    import multiprocessing as mp

    print_q = mp.SimpleQueue()

    # assume first camera group only for this test
    cam_group_idx = 0

    # create senders
    verbose = True
    skaimot_sender = TcpSenderMP('127.0.0.1', SkaimotMsg.ports[cam_group_idx], print_q, verbose=verbose)
    pose_sender = TcpSenderMP('127.0.0.1', PoseMsg.ports[cam_group_idx], print_q, verbose=verbose)
    feetpos_sender = TcpSenderMP('127.0.0.1', FeetPosMsg.ports[cam_group_idx], print_q, verbose=verbose)

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

    num_send_times = 10
    for i in range(num_send_times):
        skaimot_sender.send(skaimot_bytes)
        pose_sender.send(pose_bytes)
        feetpos_sender.send(feet_bytes)
        if not print_q.empty():
            while not print_q.empty():
                print(sender.print_q.get())

  
    print('end')
