#!/usr/bin/python3
import time
from pathlib import Path
from argparse import ArgumentParser

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import TcpSender
from skaimsginterface.udp import UdpSender


def create_example_tracksindealership(num_people=5):
    msg = TracksInDealershipMsg.new_msg()

    camera_mac = '00:10:FA:66:42:11'
    camera_id = SkaiMsg.convert_mac_addr_to_camera_identifier_number(camera_mac)
    fake_camera_ids = [camera_id] * 3 # example 3 cameras for test
    timestamp = int(time.time() * 1e9)  # integer version of double * 1e9
    example_feetpos = [420, 69.2, 0]
    example_orientation = [1.3, 4.5, 7.8]
    example_tags = ['elite_janitor_vp', 'associate_to_the_regional_manager']
    
    msg.timestamp = timestamp   

    for person_count in range(num_people):
        person = msg.people.add()
        person.id = person_count+1
        person.classification = SkaiMsg.CLASSIFICATION.EMPLOYEE
        FeetPosMsg.set_feet_pos(person, example_feetpos)
        PoseMsg.set_orientation(person, example_orientation)
        person.camera_ids.extend(fake_camera_ids)
        person.skaimot_person_tags.extend(example_tags)

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

    msg = create_example_tracksindealership()

    # write example message to file for viewing
    if args.exampleout:
        filename = 'example_msg_prints/tracks_in_dealership.txt'
        print(f'wrote example message to {filename}')
        p = Path(filename)
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_text(f'{msg}')

    msg_bytes = TracksInDealershipMsg.pack(msg, verbose=True)
    cam_group_idx = args.camgroup
    if args.udp_or_tcp == 'udp':
        sender = UdpSender(
            '127.0.0.1', TracksInDealershipMsg.ports[cam_group_idx], verbose=True)
    else:
        sender = TcpSender(
            '127.0.0.1', TracksInDealershipMsg.ports[cam_group_idx], verbose=True)
    sender.send(msg_bytes)
