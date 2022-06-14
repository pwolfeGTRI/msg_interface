#!/usr/bin/python3
import time
import types
import threading
import socketserver
import struct
from skaimsginterface.skaimessages import *


class MyMultiportUdpListener:

    def __init__(self, portlist, multiport_callback_func, verbose=False):
        """skai multiport udp listener

        def example_multiport_callback_func(data, server_address):
            # store it, unpack, etc do as you wish
            msg_type, msg = SkaiMsg.unpack(data)
            print(f'got some data length {len(data)} from {server_address} msg type {msg_type}\n')

        Args:
            portlist (list): ports to listen to 
            multiport_callback_func (types.FunctionType): your function, which should have params (data, server_address)
            verbose (bool, optional): controls additional print statements. Defaults to False.
        """
        self.verbose = verbose
        self.portlist = portlist
        self.multiport_callback_func = multiport_callback_func
        self.start_listeners()

    def start_udpserv(self, port):
        self.MySinglePortListener(('0.0.0.0', port), self)

    def start_listeners(self):
        # create threads to listen on each port
        self.threads = [
            threading.Thread(target=self.start_udpserv, args=(p, ))
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

    class MySinglePortListener(socketserver.ThreadingUDPServer):

        class MyUDPHandler(socketserver.BaseRequestHandler):

            def handle(self):
                data = self.request[0].strip()
                socket = self.request[1]

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
            socketserver.ThreadingUDPServer.allow_reuse_address = True

            # instantiate server
            socketserver.ThreadingUDPServer.__init__(self, server_address,
                                                     self.MyUDPHandler)

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
    print(
        f'got some data length {len(data)} from {server_address} msg type {msg_type}\n'
    )


if __name__ == '__main__':
    # ports to listen to
    camgroup_idx = 22
    ports = [
        SkaimotMsg.ports[camgroup_idx], PoseMsg.ports[camgroup_idx],
        FeetPosMsg.ports[camgroup_idx], LocalTrackMsg.ports[camgroup_idx],
        GlobalTrackMsg.ports[camgroup_idx], ActionMsg.ports[camgroup_idx]
    ]

    # listen
    MyMultiportUdpListener(
        portlist=ports,
        multiport_callback_func=example_multiport_callback_func)

    # stay active until ctrl+c input
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('exiting now...')