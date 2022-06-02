#!/usr/bin/python3

import time
import math

import threading
import socketserver
import struct

from skaimsginterface.skaimessages import *

class MultiportTcpListener:

    def __init__(self, portlist, multiport_callback_func, verbose=False):
        """_summary_

        Args:
            portlist (_type_): ports to listen to 
            multiport_callback_func (_type_):  your function, which should have params (data, server_address)
            verbose (bool, optional): _description_. Defaults to False.

        Raises:
            TypeError: _description_
            TypeError: _description_
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

        # initialize
        self.verbose = verbose
        self.portlist = portlist
        self.multiport_callback_func = multiport_callback_func
        self.start_listeners()

    def start_server(self, port):
        self.SinglePortListener(('0.0.0.0', port), self)

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

    def multiport_callback(self, data, server_address):
        self.multiport_callback_func(data, server_address)

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

                    # otherwise parse the length
                    length = struct.unpack('!I', bytes_in)[0]
                    # print(f'decoded length of message to be {length} bytes')

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
                    self.server.single_port_callback(data)

        def __init__(self, server_address, multiport_listener):
            # store reference to parent class
            self.multiport_listener = multiport_listener

            # turn on allow reuse ports
            socketserver.ThreadingTCPServer.allow_reuse_address = 1

            # instantiate server
            socketserver.ThreadingTCPServer.__init__(self, server_address,
                                                     self.RequestHandler)

            # now serve forever
            print(f'now listening on {self.server_address}')
            self.serve_forever()

        def single_port_callback(self, data):
            # do something single port wise if you want here...
            # otherwise pass data to higher server
            self.multiport_listener.multiport_callback(data,
                                                       self.server_address)


def example_multiport_callback_func(data, server_address):
    # store it, unpack, etc do as you wish
    msg_type, msg = SkaiMsg.unpack(data)
    print(f'got some data length {len(data)} from {server_address} msg type {msg_type}\n')


if __name__ == '__main__':
    # ports to listen to
    camgroup_idx = 0
    ports = [SkaimotMsg.ports[camgroup_idx], PoseMsg.ports[camgroup_idx], FeetPosMsg.ports[camgroup_idx]]

    # listen
    MultiportTcpListener(portlist=ports, multiport_callback_func=example_multiport_callback_func)

    # stay active until ctrl+c input
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('exiting now...')
