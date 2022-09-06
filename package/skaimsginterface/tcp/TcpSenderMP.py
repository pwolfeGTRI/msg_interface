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

    def stop(self):
        self.print_q.put('setting sender stop event!')
        self.stop_event.set()

    def start_sender_process(self):
        port = self.destination[1]
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
        self.sender_proc.daemon = True
        self.sender_proc.start()

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
                if stop_event.is_set():
                    print_q.put('stop event set')
                    break
        
        if not connected:
            print_q.put(f'failed connect attempt to {destination}!')
        else:
            print_q.put(f'successfully connected to {destination}!')
        
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
                            # print_q.put(
                            #     f'sent { SkaiMsg.getMessageTypeName(msg_bytes)} message bytes with length {len(msg_bytes)}'
                            # )
                            print_q.put(f'sent message to {destination}')
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

    
    from examples.test_skaimot import create_example_skaimotmsg
    skaimotmsg = create_example_skaimotmsg()
    skaimotmsg_bytes = SkaimotMsg.pack(skaimotmsg)

    from examples.test_pose import create_example_posemsg
    posemsg = create_example_posemsg()
    posemsg_bytes = PoseMsg.pack(posemsg)

    from examples.test_feetpos import create_example_feetposmsg
    feetmsg = create_example_feetposmsg()
    feetmsg_bytes = FeetPosMsg.pack(feetmsg)
    


    num_send_times = 3
    intermsg_delay = 0.0000001
    for i in range(num_send_times):
        skaimot_sender.send(skaimotmsg_bytes)
        # pose_sender.send(posemsg_bytes)
        # feetpos_sender.send(feetmsg_bytes)
        if not print_q.empty():
            while not print_q.empty():
                print(print_q.get())
            # time.sleep(intermsg_delay)

    print('waiting 5 before sending burst again')
    time.sleep(5)
    for i in range(num_send_times):
        skaimot_sender.send(skaimotmsg_bytes)
        # pose_sender.send(posemsg_bytes)
        # feetpos_sender.send(feetmsg_bytes)
        if not print_q.empty():
            while not print_q.empty():
                print(print_q.get())
        # time.sleep(intermsg_delay)
    
    
    # stay active until ctrl+c input
    try:
        while True:
            if not print_q.empty():
                print(print_q.get())
    except KeyboardInterrupt:
        print('exiting now...')
        
        # wait a second
        time.sleep(1)

        # print remaining print_q?
        while not print_q.empty():
            print(print_q.get())

    finally:
        skaimot_sender.stop()
        pose_sender.stop()
        feetpos_sender.stop()
  
    print('end')
