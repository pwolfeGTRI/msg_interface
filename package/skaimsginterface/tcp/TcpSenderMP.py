#!/usr/bin/python3

import hashlib
import socket
import struct
import time

from skaimsginterface.skaimessages import *
import multiprocessing as mp
import threading

import logging
log_format = logging.Formatter('%(asctime)s [%(levelname)8s] %(message)s')
log_fh = logging.FileHandler('sender_mp.log', mode='w')
log_fh.setFormatter(log_format)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)
logger.addHandler(log_fh)

class TcpSenderMP:

    ipv4_localhost = '127.0.0.1'
    ipv6_localhost = '::1' # expands to 0:0:0:0:0:0:0:1, listen on '::' for receiving
    
    def __init__(self,
                 host_ip,
                 port,
                 print_q=None,
                 retryLimit=None,
                 reconnectRetryLimit=None,
                 retryTimeoutSec=2,
                 block_during_first_connection=True,
                 ipv6=False, # default to ipv4
                 verbose=False) -> None:
        self.ipv6 = ipv6
        self.verbose = verbose
        self.retryLimit = retryLimit
        self.reconnectRetryLimit = reconnectRetryLimit
        self.retryTimeoutSec = retryTimeoutSec
        self.block_during_first_connection = block_during_first_connection 

        # create stop event ,print queue, sender queue
        self.stop_event = mp.Event()
        self.first_connection_event = mp.Event()
        self.connected_event = mp.Event()
        self.pause_event = mp.Event()
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
            self.first_connection_event,
            self.connected_event,
            self.print_q,
            self.sock,
            self.destination,
            self.retryLimit,
            self.retryTimeoutSec,
            self.block_during_first_connection,
            self.verbose)

        # start sender process
        self.start_sender_process()

    def stop(self):
        if self.print_q is not None:
            printmsg = 'setting sender stop event!'
            logger.info(printmsg)
            self.print_q.put(printmsg)
        self.stop_event.set()

    '''
    return whether the sender is connected
    '''
    def is_connected(self):
        return self.connected_event.is_set()

    '''
    return whether the sender process is alive
    '''
    def is_alive(self):
        return self.sender_proc.is_alive()

    '''
    return whether the sender process is paused due to exceeding the reconnect retry limit
    '''
    def is_paused(self):
        return self.pause_event.is_set()
    
    '''
    resume a paused sender process
    '''
    def resume(self):
        self.pause_event.clear()

    def start_sender_process(self):
        port = self.destination[1]
        self.sender_proc = mp.Process(
            name=f'TcpSender_{port}',
            target=self.sender_process,
            args=(
                self.stop_event,
                self.first_connection_event,
                self.connected_event,
                self.pause_event,
                self.print_q,
                self.send_q,
                self.sock,
                self.destination,
                self.reconnectRetryLimit,
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
        send_timeout_sec = 0.0
        sock.settimeout(send_timeout_sec)
        return sock

    @staticmethod
    def try_to_connect(print_q, sock, destination, retryTimeoutSec, verbose):
        success = False
        try:
            sock.connect(destination)
            printmsg = f'connected to {destination}!'
            logger.info(printmsg)
            if print_q is not None:
                print_q.put(printmsg)
            success = True

        except ConnectionRefusedError:
            printmsg = f'{destination} connection refused'
            logger.info(printmsg)
            if print_q is not None:
                print_q.put(printmsg)

        except Exception as e:
            printmsg = f'TcpSenderMP try_to_connect exception: {e}'
            logger.info(printmsg)
            if print_q is not None:
                print_q.put(printmsg)

        if not success:
            printmsg = f'trying to connect to {destination} again in {retryTimeoutSec} seconds'
            logger.info(printmsg)
            if print_q is not None:
                print_q.put(printmsg)
            time.sleep(retryTimeoutSec)

        return success

    @staticmethod
    def connect_to_destination(stop_event, 
                               first_connection_event,
                               connected_event,
                               print_q, 
                               sock, 
                               destination, 
                               retryLimit, 
                               retryTimeoutSec, 
                               block_during_first_connection,
                               verbose):
        if not block_during_first_connection:
            connect_thread = threading.Thread(
                target=TcpSenderMP.connect_to_destination, 
                args=(stop_event, first_connection_event, connected_event, print_q, sock, destination, retryLimit, retryTimeoutSec, verbose, True))
            connect_thread.daemon = True
            connect_thread.start()
        else:
            # attempt to connect once
            connected = False
            if retryLimit is None:
                while (not connected) and (not stop_event.is_set()):
                    try:
                        connected = TcpSenderMP.try_to_connect(print_q, sock, destination, retryTimeoutSec, verbose)
                    except Exception as e:
                        printmsg = f'connection to {destination} exception: {e}'
                        logger.info(printmsg)
                        if print_q is not None:
                            print_q.put(printmsg)
            else:
                for i in range(retryLimit):
                    connected = TcpSenderMP.try_to_connect(print_q, sock, destination, retryTimeoutSec, verbose)
                    if stop_event.is_set():
                        printmsg = 'stop event set'
                        logger.info(printmsg)
                        if print_q is not None:
                            print_q.put(printmsg)
                        break
                    elif connected:
                        break
            
            if connected:
                connected_event.set()
                printmsg = f'successfully connected to {destination}!'
                logger.info(printmsg)
                if print_q is not None:
                    print_q.put(printmsg)

                if not first_connection_event.is_set():
                    first_connection_event.set()
            else:
                connected_event.clear()
                if retryLimit is None:
                    printmsg = f'somehow failed connect to {destination}!'
                    logger.info(printmsg)
                    if print_q is not None:
                        print_q.put(printmsg)
                else:
                    printmsg = f'failed to connect to {destination} after {retryLimit} tries!'
                    logger.info(printmsg)
                    if print_q is not None:
                        print_q.put(printmsg)

                if not first_connection_event.is_set():
                    first_connection_event.set()
                    stop_event.set()
            
            # return results of attempt to connect
            return connected

    @staticmethod
    def sender_process(stop_event,
                       first_connection_event,
                       connected_event,
                       pause_event,
                       print_q,
                       send_q,
                       sock,
                       destination,
                       retryLimit,
                       retryTimeoutSec,
                       verbose,
                       ipv6=False):
        # check if first connection is made
        while not first_connection_event.is_set():
            time.sleep(0.01)


        # send_timeout_sec = 0.8
        while not stop_event.is_set():
            
            # check if anything to send
            if not send_q.empty():
                
                # try sending until sent (handle disconnects too)
                sent = False
                while (not sent) and (not stop_event.is_set()):
                    # attempt to send on socket
                    try:
                        # get msg bytes with checksum appended and length prepended
                        if connected_event.is_set():
                            msg_bytes_with_checksum_and_length = send_q.get()
                        else:
                            printmsg = 'connected event not set!'
                            logger.info(printmsg)
                            if print_q is not None:
                                print_q.put(printmsg)
                            raise BrokenPipeError
                        
                        logger.info(f'sending {len(msg_bytes_with_checksum_and_length)} bytes...')
                        sock.sendall(msg_bytes_with_checksum_and_length)
                        if verbose:
                            printmsg = f'sent message to {destination}'
                            logger.info(printmsg)
                            if print_q is not None:
                                print_q.put(printmsg)
                        sent = True

                    except BrokenPipeError:
                        connected_event.clear()
                        printmsg = f'{destination} connection broken! reconnecting...'
                        logger.error(printmsg)
                        if print_q is not None:
                            print_q.put(printmsg)

                        # close, recreate, and try to reconnect
                        sock.close()
                        sock = TcpSenderMP.create_socket(ipv6=ipv6)
                        connected = TcpSenderMP.connect_to_destination(
                            stop_event,
                            first_connection_event,
                            connected_event,
                            print_q,
                            sock,
                            destination,
                            retryLimit,
                            retryTimeoutSec,
                            True,
                            verbose)
                        
                        # pause the thread and resume when pause_event is unset
                        if not connected:
                            printmsg = f'pausing sender process due to {retryLimit} unsuccessful reconnect attempts'
                            logger.info(printmsg)
                            if print_q is not None:
                                print_q.put(printmsg)
                            pause_event.set()
                            time.sleep(0.5)
                            while pause_event.is_set():
                                time.sleep(0.1)

                    except Exception as e:
                        if print_q is not None:
                            print_q.put(f'TcpSenderMP Exception: {e}')

                    if not sent:
                        if print_q is not None:
                            print_q.put('msg not sent. retrying...')
           
                # delay between repeated sends
                time.sleep(0.005)

    def send(self, msg_bytes, send_failed_checksum=False):
        # calc checksum 
        clean_checksum = hashlib.md5(msg_bytes).digest()
        # if you want to send a intentionally false checksum then mutate the bytes
        if send_failed_checksum:
            # add 1 to each bytes
            checksum = b''
            for b in clean_checksum:
                checksum += bytes([ min(255, max(b+1, 0)) ])
        else:
            checksum = clean_checksum
        # and append
        msg_bytes_with_checksum = msg_bytes + checksum
        # calc length and prepend
        msg_bytes_with_checksum_and_length = struct.pack('!I', len(msg_bytes_with_checksum)) + msg_bytes_with_checksum
        # add to send queue to be sent
        self.send_q.put(msg_bytes_with_checksum_and_length)
        
if __name__ == '__main__':

    def read_print_q(print_q):
        while True:
            if not print_q.empty():
                while not print_q.empty():
                    print(print_q.get())

    print_q = mp.SimpleQueue()

    # assume first camera group only for this test
    cam_group_idx = 45

    # create senders
    verbose = True
    skaimot_sender = TcpSenderMP('127.0.0.1', SkaimotMsg.ports[cam_group_idx], print_q=print_q, verbose=verbose, retryLimit=5, reconnectRetryLimit=3, block_during_first_connection=False)
    pose_sender = TcpSenderMP('127.0.0.1', PoseMsg.ports[cam_group_idx], print_q, verbose=verbose, retryLimit=5, block_during_first_connection=False)
    feetpos_sender = TcpSenderMP('127.0.0.1', FeetPosMsg.ports[cam_group_idx], print_q, verbose=verbose, retryLimit=5, block_during_first_connection=False)

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

    # start print_q reading thread
    t_print_q = threading.Thread(target=read_print_q, args=(print_q,))
    t_print_q.daemon = True
    t_print_q.start()

    # stay active until ctrl+c input
    num_send_times = 3
    # intermsg_delay = 0.001
    try:
        while True:
            for i in range(num_send_times):
                if skaimot_sender.is_connected():
                    # if connection goes down, messages will still be queued
                    skaimot_sender.send(skaimotmsg_bytes)
                else:
                    print('skaimot sender is not connected')

                if skaimot_sender.is_paused():
                    print('skaimot sender is paused! unpausing in 10s')
                    time.sleep(10)
                    skaimot_sender.resume()
                # time.sleep(intermsg_delay)
                # pose_sender.send(posemsg_bytes)
                # feetpos_sender.send(feetmsg_bytes)
                # time.sleep(intermsg_delay)

            print('waiting 2 before sending burst again')
            time.sleep(2)

            # skaimot_sender.send(skaimotmsg_bytes)
            # time.sleep(2)
            # skaimot_sender.send(skaimotmsg_bytes)
            # time.sleep(2)
            # skaimot_sender.stop()

            # while skaimot_sender.is_alive():
            #     print('sender is alive')
            #     time.sleep(0.1)            

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
        # pass
  
    print('end')
