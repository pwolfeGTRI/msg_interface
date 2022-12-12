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
    
    fake_global_ids = [39, 69, 42]
    num_cams_per_person = len(fake_global_ids) # i dunno it depends on the person
    fake_camera_ids = [camera_id] * num_cams_per_person

    fake_vehicle_global_id = 10
    example_vehicle_tags = ['1234567', 'blue sedan']

    timestamp = int(time.time() * 1e9)  # integer version of double * 1e9
    example_feetpos = [420, 69.2, 0]
    example_orientation = [1.3, 4.5, 7.8]
    example_person_tags = ['elite_janitor_vp', 'associate_to_the_regional_manager']
    fake_tlbr_box = [0.2, 0.2, 0.2, 0.2]
    
    msg.timestamp = timestamp   

    for person_count in range(num_people):
        person = msg.people.add()
        person.id = person_count+1
        person.classification = SkaiMsg.CLASSIFICATION.EMPLOYEE
        FeetPosMsg.set_feet_pos(person, example_feetpos)
        PoseMsg.set_orientation(person, example_orientation)        
        person.skaimot_person_tags.extend(example_person_tags)

        for cam_count in range(num_cams_per_person):
            global_bbox = person.boxes.add()
            global_bbox.global_id = fake_global_ids[cam_count]
            global_bbox.camera_id = fake_camera_ids[cam_count]
            global_bbox.top = fake_tlbr_box[0]
            global_bbox.left = fake_tlbr_box[1]
            global_bbox.bottom = fake_tlbr_box[2]
            global_bbox.right = fake_tlbr_box[3]

    vehicle = msg.vehicles.add()
    vehicle.id = fake_vehicle_global_id
    vehicle.object_tags.extend(example_vehicle_tags)

    for cam_count in range(num_cams_per_person):
            global_bbox = vehicle.boxes.add()
            global_bbox.global_id = fake_vehicle_global_id
            global_bbox.camera_id = fake_camera_ids[cam_count]
            global_bbox.top = fake_tlbr_box[0]
            global_bbox.left = fake_tlbr_box[1]
            global_bbox.bottom = fake_tlbr_box[2]
            global_bbox.right = fake_tlbr_box[3]


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
    dealership_test_idx = 4
    if args.udp_or_tcp == 'udp':
        sender = UdpSender(
            '127.0.0.1', TracksInDealershipMsg.ports[dealership_test_idx], verbose=True)
    else:
        sender = TcpSender(
            '127.0.0.1', TracksInDealershipMsg.ports[dealership_test_idx], verbose=True)
    sender.send(msg_bytes)
