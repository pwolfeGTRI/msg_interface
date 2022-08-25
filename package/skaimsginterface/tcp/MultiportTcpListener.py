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

import code

class MultiportTcpListener:

    def __init__(self, portlist, multiport_callback_func, ipv6=False, verbose=False, recordfile=None):
        """skai multiport TCP listener

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

        # initialize file recorder if recordfile specified
        self.recorder = None
        if recordfile is not None:
            print('opening recorder...')
            self.recorder = FileRecorder(recordfile)
            self.recorder.open()

        # initialize
        self.verbose = verbose
        self.portlist = portlist
        self.multiport_callback_func = multiport_callback_func
        self.ipv6 = ipv6
        if self.ipv6:
            self.listen_addr = '::'
        else:
            self.listen_addr = '0.0.0.0'
        self.start_listeners()

    def __del__(self):
        # initialize file recorder if recordfile specified
        if self.recorder is not None:
            print('closing recorder...')
            self.recorder.close()
    
    def start_server(self, port):
        self.SinglePortListener((self.listen_addr, port), self)

    def start_listeners(self):
        # create threads sto listen on each port
        self.threads = [
            threading.Thread(target=self.start_server, args=(p, ))
            for p in self.portlist
        ]

        # start them
        if self.verbose:
            print('starting threads...')
        for t in self.threads:
            t.daemon = True  # non blocking
            t.start()

    def multiport_callback(self, data, server_address, firstpacket_timestamp):
        msg, checksum = data[:-16], data[-16:]
        msg_checksum = hashlib.md5(msg).digest()

        if checksum == msg_checksum:
            if self.recorder is not None:    
                port = server_address[1]
                if self.verbose:
                    print(f'recording msg length {len(msg)} on port: {port} firstpacket_ts {firstpacket_timestamp}')
                self.recorder.record(msg, firstpacket_timestamp, port)

            self.multiport_callback_func(msg, server_address)

        elif self.verbose:
            print('checksum failed')


    class SinglePortListener(socketserver.ThreadingTCPServer):

        class RequestHandler(socketserver.BaseRequestHandler):

            def handle(self):
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

                    # send back message in uppercase as confirmation (comment out if not needed)
                    # socket.sendto(data.upper(), self.client_address)

                    # call server callback function with data
                    self.server.single_port_callback(data, firstpacket_timestamp)

        def __init__(self, server_address, multiport_listener):
            # store reference to parent class
            self.multiport_listener = multiport_listener

            # turn on allow reuse ports
            socketserver.ThreadingTCPServer.allow_reuse_address = True

            # switch to ipv6 family if set in multiport listener class
            if multiport_listener.ipv6:
                self.address_family = socket.AF_INET6

            # instantiate server
            socketserver.ThreadingTCPServer.__init__(self, server_address,
                                                     self.RequestHandler)

            # now serve forever
            print(f'now listening on {self.server_address}')
            self.serve_forever()

        def single_port_callback(self, data, firstpacket_timestamp):
            # do something single port wise if you want here...
            # otherwise pass data to higher server
            self.multiport_listener.multiport_callback(data,
                                                       self.server_address, firstpacket_timestamp)


def example_multiport_callback_func(data, server_address):
    # store it, unpack, etc do as you wish
    msg_type, msg = SkaiMsg.unpack(data)
    print(
        f'got some data length {len(data)} from {server_address} msg type {msg_type}\n'
    )


if __name__ == '__main__':
    # ports to listen to
    camgroup_idx = 0
    ports = [
        SkaimotMsg.ports[camgroup_idx], PoseMsg.ports[camgroup_idx],
        FeetPosMsg.ports[camgroup_idx], LocalTrackMsg.ports[camgroup_idx],
        GlobalTrackMsg.ports[camgroup_idx], ActionMsg.ports[camgroup_idx]
    ]

    # listen
    MultiportTcpListener(
        portlist=ports,
        multiport_callback_func=example_multiport_callback_func)

    # stay active until ctrl+c input
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('exiting now...')
