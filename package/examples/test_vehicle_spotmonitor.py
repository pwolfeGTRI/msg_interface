#!/usr/bin/python3
import time
from pathlib import Path
from argparse import ArgumentParser

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import TcpSender
from skaimsginterface.udp import UdpSender


SKAIMSGCLASS = VehicleSpotMonitorMsg

def create_example_vehiclespotmonitormsg(num_vehicles=2, num_cams=5):
    camera_mac = '00:10:FA:66:42:11'
    camera_id = SkaiMsg.convert_mac_addr_to_camera_identifier_number(camera_mac)
    timestamp = int(time.time() * 1e9)  # integer version of double * 1e9

    msg = SKAIMSGCLASS.new_msg()
    msg.timestamp = timestamp
            
    return msg


if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument('udp_or_tcp', type=str, help='protocol to listen on', choices=('tcp', 'udp'))
    parser.add_argument('--exampleout', help='dump an example message text file under a folder example_msg_prints', nargs='?', type=bool, const=True, default=False)
    parser.add_argument('--camgroup', help='camera group number (default 0)', nargs='?', type=int, default=0)
    args = parser.parse_args()

    msg = create_example_vehiclespotmonitormsg()

    # write example message to file for viewing
    if args.exampleout:
        filename = 'example_msg_prints/vehiclespotmonitor.txt'
        print(f'wrote example message to {filename}')
        p = Path(filename)
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_text(f'{msg}')
    
    msg_bytes = SKAIMSGCLASS.pack(msg, verbose=True)
    cam_group_idx = args.camgroup
    if args.udp_or_tcp == 'udp':
        sender = UdpSender('127.0.0.1', SKAIMSGCLASS.ports[cam_group_idx], verbose=True)
    else:    
        sender = TcpSender('127.0.0.1', SKAIMSGCLASS.ports[cam_group_idx], verbose=True)
    sender.send(msg_bytes)

