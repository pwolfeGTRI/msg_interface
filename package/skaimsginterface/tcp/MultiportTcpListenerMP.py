#!/usr/bin/python3

import hashlib
import time
import math

import threading
import socketserver
import socket
import struct

from skaimsginterface.skaimessages import *
from skaimsginterface.replay import FileRecorder

import multiprocessing as mp

import code

import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)8s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='Listener.log',
                    filemode='w')

class MultiportTcpListenerMP:

    def __init__(self, portlist, multiport_callback_func, print_q=None, ipv6=False, verbose=False, recordfile=None):
        """skai multiport TCP listener using multiprocessing

        Args:
            portlist (list): ports to listen to 
            multiport_callback_func (_type_):  your function, which should have params (data, server_address)
            ipv6 (bool): default val=False, defaults to using ipv4
            verbose (bool, optional): _description_. Defaults to False.
        """
        # type checking
        if isinstance(portlist, int):
            portlist = [portlist]
        if not isinstance(portlist, list):
            raise TypeError(
                'portlist must be a list of integers or a single port integer')
        for p in portlist:
            if not isinstance(p, int):
                raise TypeError(
                    'portlist must be a list of integers or a single port integer'
                )

        # Create MPC Queue, stop event, print queue for multiprocessing
        self.msg_q = mp.SimpleQueue()
        self.print_q = print_q #mp.SimpleQueue()
        self.stop_event = mp.Event()

        # initialize file recorder queue & file recorder if recordfile specified
        self.record_q = None
        if recordfile is not None:
            self.record = True
            
            self.record_q = mp.SimpleQueue()
            self.record_proc = mp.Process(
                name='record_process',
                target=FileRecorder.mp_record_process,
                args=(self.stop_event, self.print_q, self.record_q, recordfile, False)
            )
            self.record_proc.daemon = True
            self.record_proc.start()

        # initialize
        self.verbose = verbose
        self.portlist = portlist
        self.user_multiport_callback = multiport_callback_func
        self.ipv6 = ipv6
        if self.ipv6:
            self.listen_addr = '::'
        else:
            self.listen_addr = '0.0.0.0'

        # start listening
        self.start_listeners()


    @staticmethod
    def multiport_process(stop_event, print_q, msg_q, user_multiport_callback, record_q):
        while not stop_event.is_set():
            if not msg_q.empty():
                # grab msg off queue
                msg_bytes, firstpacket_timestamp, server_address = msg_q.get()
                
                # record 
                if record_q is not None:
                    # msg_bytes, epoch_timestamp, port
                    port = server_address[1]
                    record_q.put( (msg_bytes, firstpacket_timestamp, port) )
                
                # forward msg_bytes to user callback
                user_multiport_callback(msg_bytes, server_address)


    @staticmethod
    def single_port_process(stop_event, print_q, msg_q, addr_port:tuple, ListenerClass):
        # instantiate listener
        spl = ListenerClass(addr_port, print_q, msg_q)

        # now listen for messages on port until stop event
        if print_q is not None:
            print_q.put(f'now listening on {addr_port}...')
        try:
            while not stop_event.is_set():
                spl.handle_request()
        except Exception as e:
            if print_q is not None:
                print_q.put(f'something went wrong in single port request handling: {e}')
        finally:
            # close server after stop event
            spl.server_close()

    def start_listeners(self):
                
        # start multiport process
        self.multiport_proc = mp.Process(
            name='mp_msg_receiver',
            target=self.multiport_process,
            args=(self.stop_event, self.print_q, self.msg_q, self.user_multiport_callback, self.record_q, )
        )
        self.multiport_proc.daemon = True
        self.multiport_proc.start()

        # start single port processes
        self.processes = []
        for port in self.portlist:
            listen_addr_port = (self.listen_addr, port)
            proc = mp.Process(
                name=f'listener_port_{port}',
                target=self.single_port_process,
                args=(self.stop_event, self.print_q, self.msg_q, listen_addr_port, self.SinglePortListener)
            )
            proc.daemon = True
            proc.start()
            self.processes.append(proc)

    def stop(self):
        self.stop_event.set()

    class SinglePortListener(socketserver.ThreadingTCPServer):

        class RequestHandler(socketserver.BaseRequestHandler):

            def handle(self):
                try:
                    # note: socket will close at end of handle method
                    while True:

                        # assumes first 4 bytes designate length of message
                        # (packed as network endian unsigned int)
                        bytes_in = self.request.recv(4)
                        if not bytes_in:
                            continue  # continue if no new message

                        # otherwise log timestamp of first packet arrival
                        firstpacket_timestamp = time.time()

                        # and parse the length
                        length = struct.unpack('!I', bytes_in)[0]

                        # receive in chunks
                        chunksize = 4096
                        data = bytes()
                        for chunk in range(math.ceil(length / chunksize)):
                            data += self.request.recv(chunksize)

                        # variables = globals().copy()
                        # variables.update(locals())
                        # shell = code.InteractiveConsole(variables)
                        # shell.interact()

                        # socket = self.request.getsockname()
                        # print(
                        #     f'client {self.client_address}\n\twrote {data}\n\tto {self.server.server_address}'
                        # )

                        # verify checksum
                        msg_bytes, checksum_bytes = data[:-16], data[-16:]
                        computed_checksum = hashlib.md5(msg_bytes).digest()

                        # pass onwards if verified, otherwise add an error msg to print_q
                        if checksum_bytes == computed_checksum:
                            # pass to msg queue
                            self.server.msg_q.put( (msg_bytes, firstpacket_timestamp, self.server.server_address) )
                        else:
                            if self.server.print_q is not None:
                                self.server.print_q.put(f'checksum failed on {self.server.server_address}')
                except Exception as e:
                    self.server.print_q.put(f'handle failed...logging the exception')
                    logging.exception(f'Handling Exception: {e}')

        def __init__(self, server_address, print_q, msg_q, ipv6=False):
            # store reference to mp vars
            self.print_q = print_q
            self.msg_q = msg_q

            # turn on allow reuse ports
            socketserver.ThreadingTCPServer.allow_reuse_address = True

            # switch to ipv6 family if set in multiport listener class
            if ipv6:
                self.address_family = socket.AF_INET6

            # instantiate server
            socketserver.ThreadingTCPServer.__init__(self, server_address,
                                                     self.RequestHandler)

      



def example_multiport_callback_func(msg_bytes, server_address):
    # store it, unpack, etc do as you wish
    msg_type, msg = SkaiMsg.unpack(msg_bytes)
    print(
        f'got some data length {len(msg_bytes)} from {server_address} msg type {msg_type}\n'
    )


if __name__ == '__main__':
    
    # ports to listen to
    camgroup_idx = 0
    ports = [
        SkaimotMsg.ports[camgroup_idx], PoseMsg.ports[camgroup_idx],
        FeetPosMsg.ports[camgroup_idx], LocalTrackMsg.ports[camgroup_idx],
        GlobalTrackMsg.ports[camgroup_idx], ActionMsg.ports[camgroup_idx]
    ]

    # make mp print q
    print_q = mp.SimpleQueue()

    # start listening
    mpl = MultiportTcpListenerMP(
        portlist=ports,
        multiport_callback_func=example_multiport_callback_func,
        print_q=print_q)

    # stay active until ctrl+c input
    try:
        while True:
            if not print_q.empty():
                print(print_q.get())
            time.sleep(0.001)
    except KeyboardInterrupt:
        print('exiting now...')
        mpl.stop() 
