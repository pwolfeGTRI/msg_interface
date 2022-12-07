#!/usr/bin/python3
import time
import numpy as np
from pathlib import Path
from argparse import ArgumentParser

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import TcpSender
from skaimsginterface.udp import UdpSender

dealership_test_idx = 4

def create_example_module_status(module_enum, connection_status, error_msg=None):
    msg = ModuleStatusMsg.new_msg()
    timestamp = int(time.time() * 1e9)  # integer version of double * 1e9

    msg.module = SkaiMsg.ADAT_MODULE.GLOBAL_TRACK_HANDLER
    
    # event manager connections added like this
    em_connection = msg.connections.add()
    em_connection.connection_name = 'TracksInDealership'
    em_connection.destination_module = SkaiMsg.ADAT_MODULE.EVENT_MANAGER
    em_connection.port = TracksInDealershipMsg.ports[dealership_test_idx]
    em_connection.status = SkaiMsg.CONNECTION_STATUS.CONNECTING

    # errors added like this
    if error_msg is not None:
        example_error = msg.errors.add()
        example_error.timestamp = timestamp
        example_error.error_msg = error_msg

def create_example_adat_status():
    msg = AdatStatusMsg.new_msg()


if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument('udp_or_tcp', type=str, help='protocol to listen on', choices=('tcp', 'udp'))
    parser.add_argument('--exampleout', help='dump an example message text file under a folder example_msg_prints', nargs='?', type=bool, const=True, default=False)
    parser.add_argument('--camgroup', help='camera group number (default 0)', nargs='?', type=int, default=0)
    parser.add_argument('--ipv6', help='use ipv6 instead of ipv4 default', nargs='?', type=bool, const=True, default=False)
    args = parser.parse_args()

    msg_module = create_example_module_status()
    msg_adat = create_example_adat_status()
    
    # write example message to file for viewing
    if args.exampleout:
        filename = 'example_msg_prints/skaimot.txt'
        print(f'wrote example message to {filename}')
        p = Path(filename)
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_text(f'{msg}')

    bytes_module = ModuleStatusMsg.pack(msg_module, verbose=True)
    bytes_adat = AdatStatusMsg.pack(msg_adat, verbose=True)
    # cam_group_idx = args.camgroup

    if args.ipv6:
        destination_ip = '::1' # TcpSender.ipv6_localhost
    else:
        destination_ip = TcpSender.ipv4_localhost
    
    if args.udp_or_tcp == 'udp':
        sender_module = UdpSender(destination_ip, ModuleStatusMsg.ports[dealership_test_idx], verbose=True)
        sender_adat = UdpSender(destination_ip, AdatStatusMsg.ports[dealership_test_idx], verbose=True)
    else:    
        sender_module = TcpSender(destination_ip, ModuleStatusMsg.ports[dealership_test_idx], ipv6=args.ipv6, verbose=True)
        sender_adat = TcpSender(destination_ip, AdatStatusMsg.ports[dealership_test_idx], ipv6=args.ipv6, verbose=True)
    
    sender_module.send(bytes_module)
    sender_adat.send(bytes_adat)
