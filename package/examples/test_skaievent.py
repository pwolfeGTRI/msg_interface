#!/usr/bin/python3
import time
from pathlib import Path
from argparse import ArgumentParser

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import TcpSender
from skaimsginterface.udp import UdpSender


def create_example_skaievent(num_associated_objs=2, num_cams=3):
    msg = SkaiEventMsg.new_msg()

    timestamp = int(time.time() * 1e9)  # integer version of double * 1e9
    example_location_tags = ['showroom', 'front_desk']
    camera_mac = '00:10:FA:66:42:11'
    camera_id = SkaiMsg.convert_mac_addr_to_camera_identifier_number(camera_mac)
    fake_camera_ids = [camera_id] * 3 # example 3 cameras for test
    example_event_confidence = 0.80

    msg.event = 2 #customer_greeted
    msg.confidence = example_event_confidence
    msg.event_starttime = timestamp
    msg.event_endtime = timestamp + 10
    msg.location_tags.extend(example_location_tags)

    msg.primary_obj.global_id = 69
    msg.primary_obj.classification = SkaiMsg.CLASSIFICATION.CUSTOMER
    msg.primary_obj.confidence = example_event_confidence # is this needed?

    for obj_count in range(num_associated_objs):
        associated_obj = msg.associated_objs.add()
        associated_obj.global_id = obj_count+1
        associated_obj.classification = SkaiMsg.CLASSIFICATION.EMPLOYEE
        associated_obj.confidence = example_event_confidence # is this needed?

    for cam_count in range(num_cams):
        camera_time_range = msg.camera_time_ranges.add()
        camera_time_range.camera_id = fake_camera_ids[cam_count]
        camera_time_range.start_timestamp = timestamp + cam_count
        camera_time_range.end_timestamp = timestamp + 10 - cam_count

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

    msg = create_example_skaievent()
    # print(msg)

    # write example message to file for viewing
    if args.exampleout:
        filename = 'example_msg_prints/skaievent.txt'
        print(f'wrote example message to {filename}')
        p = Path(filename)
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_text(f'{msg}')

    msg_bytes = SkaiEventMsg.pack(msg, verbose=True)
    cam_group_idx = args.camgroup
    if args.udp_or_tcp == 'udp':
        sender = UdpSender(
            '127.0.0.1', SkaiEventMsg.ports[cam_group_idx], verbose=True)
    else:
        sender = TcpSender(
            '127.0.0.1', SkaiEventMsg.ports[cam_group_idx], verbose=True)
    sender.send(msg_bytes)
