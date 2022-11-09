#!/usr/bin/python3
import time
from pathlib import Path
from argparse import ArgumentParser

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import TcpSender
from skaimsginterface.udp import UdpSender


SKAIMSGCLASS = VehicleMsg

def create_example_vehiclemsg(num_vehicles=2, num_cams=5):
    camera_mac = '00:10:FA:66:42:11'
    camera_id = SkaiMsg.convert_mac_addr_to_camera_identifier_number(camera_mac)
    timestamp = int(time.time() * 1e9)  # integer version of double * 1e9
    example_box = [0.2, 0.21, 0.4, 0.42] # t l b r float 0 to 1

    # create new protobuf message and load with values
    msg = SKAIMSGCLASS.new_msg()
    for cam_count in range(num_cams):
        
        # add new camera frame to the message & set frame vals
        frame = msg.camera_frames.add() 
        frame.timestamp = timestamp
        frame.camera_id = camera_id
        
        for vehicle_count in range(num_vehicles):
            vehicle = frame.vehicles.add()
            VehicleMsg.set_box_from_list(vehicle.box, example_box)
            vehicle.object_tags.extend(['example_vehicle_tag1', 'example_vehicle_tag2'])

    return msg


if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument('udp_or_tcp', type=str, help='protocol to listen on', choices=('tcp', 'udp'))
    parser.add_argument('--exampleout', help='dump an example message text file under a folder example_msg_prints', nargs='?', type=bool, const=True, default=False)
    parser.add_argument('--camgroup', help='camera group number (default 0)', nargs='?', type=int, default=0)
    args = parser.parse_args()

    msg = create_example_vehiclemsg()

    # write example message to file for viewing
    if args.exampleout:
        filename = 'example_msg_prints/vehicle.txt'
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

