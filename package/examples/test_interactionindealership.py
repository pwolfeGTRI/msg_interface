#!/usr/bin/python3
import time
from pathlib import Path
from argparse import ArgumentParser

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import TcpSender
from skaimsginterface.udp import UdpSender


def create_example_interactionindealership(num_associated_tracks=2):
    msg = InteractionInDealershipMsg.new_msg()

    camera_mac = '00:10:FA:66:42:11'
    camera_id = SkaiMsg.convert_mac_addr_to_camera_identifier_number(camera_mac)
    fake_camera_ids = [camera_id] * 3 # example 3 cameras for test
    timestamp = int(time.time() * 1e9)  # integer version of double * 1e9

    msg.timestamp = timestamp
    msg.confidence = 0.80
    msg.primary_track.id = 69
    msg.primary_track.classification = SkaiMsg.CLASSIFICATION.CUSTOMER
    msg.primary_track.camera_ids.extend(fake_camera_ids)
    msg.interaction_type = 'greeting'

    for person_count in range(num_associated_tracks):
        associated_track = msg.associated_tracks.add()
        associated_track.id = person_count+1
        associated_track.classification = SkaiMsg.CLASSIFICATION.EMPLOYEE
        associated_track.camera_ids.extend(fake_camera_ids)

    return msg


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('udp_or_tcp', type=str,
                        help='protocol to listen on', choices=('tcp', 'udp'))
    parser.add_argument('--exampleout', help='dump an example message text file under a folder example_msg_prints',
                        nargs='?', type=bool, const=True, default=False)
    parser.add_argument(
        '--camgroup', help='camera group number (default 0)', nargs='?', type=int, default=0)
    args = parser.parse_args()

    msg = create_example_interactionindealership()
    # print(msg)

    # write example message to file for viewing
    if args.exampleout:
        filename = 'example_msg_prints/interaction_in_dealership.txt'
        print(f'wrote example message to {filename}')
        p = Path(filename)
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_text(f'{msg}')

    msg_bytes = InteractionInDealershipMsg.pack(msg, verbose=True)
    cam_group_idx = args.camgroup
    if args.udp_or_tcp == 'udp':
        sender = UdpSender(
            '127.0.0.1', InteractionInDealershipMsg.ports[cam_group_idx], verbose=True)
    else:
        sender = TcpSender(
            '127.0.0.1', InteractionInDealershipMsg.ports[cam_group_idx], verbose=True)
    sender.send(msg_bytes)
