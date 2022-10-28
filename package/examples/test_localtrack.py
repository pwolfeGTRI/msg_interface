#!/usr/bin/python3

from argparse import ArgumentParser
from pathlib import Path

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import TcpSender
from skaimsginterface.udp import UdpSender


from test_skaimot import create_example_skaimotmsg
from test_pose import create_example_posemsg
from test_feetpos import create_example_feetposmsg
from test_action import create_example_actionmsg

if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument('udp_or_tcp', type=str, help='protocol to listen on', choices=('tcp', 'udp'))
    parser.add_argument('--exampleout', help='dump an example message text file under a folder example_msg_prints', nargs='?', type=bool, const=True, default=False)
    parser.add_argument('--camgroup', help='camera group number (default 0)', nargs='?', type=int, default=0)
    args = parser.parse_args()

    # create example base messages
    # assume same num people and frames, perfect aligment and everything
    camnum = 2
    peoplenum = 3
    example_skaimotmsg = create_example_skaimotmsg(peoplenum, camnum)
    example_posemsg = create_example_posemsg(peoplenum, camnum)
    example_feetposmsg = create_example_feetposmsg(peoplenum, camnum)

    # populate local track message
    msg = LocalTrackMsg.new_msg()
    skaimot_ts = example_skaimotmsg.camera_frames[0].timestamp
    msg.timestamp = skaimot_ts
    
    for skaimotframe, poseframe, feetframe in zip(example_skaimotmsg.camera_frames, example_posemsg.camera_frames, example_feetposmsg.camera_frames):
        # create new local track camera frame
        frame = msg.camera_frames.add()
        frame.camera_id = skaimotframe.camera_id

        # populate frame with people
        for skaimotperson, poseperson, feetperson in zip(skaimotframe.people_in_frame, poseframe.people_in_frame, feetframe.people_in_frame):
            person = frame.people_in_frame.add()
            
            # populate skaimot data
            person.skaimot_id = skaimotperson.id
            person.classification = skaimotperson.classification
            person.box.CopyFrom(skaimotperson.box)
            person.skaimot_person_tags.extend(skaimotperson.tags)

            # copy basic embed data & append global track handler info
            person.face_embed.CopyFrom(skaimotperson.face_embedding)
            person.face_embed.box.CopyFrom(skaimotperson.box) # copies fullbody box for now TODO update to just face in skaimot?
            person.face_embed.camera_id = frame.camera_id
            
            person.bbox_embed.CopyFrom(skaimotperson.bbox_embedding)
            person.bbox_embed.box.CopyFrom(skaimotperson.box)
            person.bbox_embed.camera_id = frame.camera_id
    
            # populate pose data
            person.pose_keypoints.CopyFrom(poseperson.keypoints)
            person.pose_orientation.CopyFrom(poseperson.orientation)

            # populate feet position data
            person.feet_position.CopyFrom(feetperson.feet_position)
            person.feet_position_confidence = feetperson.confidence
           
    # write example message to file for viewing
    if args.exampleout:
        filename = 'example_msg_prints/localtrack.txt'
        print(f'wrote example message to {filename}')
        p = Path(filename)
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_text(f'{msg}')

    msg_bytes = LocalTrackMsg.pack(msg)
    cam_group_idx = args.camgroup
    if args.udp_or_tcp == 'udp':
        sender = UdpSender('127.0.0.1', SkaimotMsg.ports[cam_group_idx], verbose=True)
    else:    
        sender = TcpSender('127.0.0.1', LocalTrackMsg.ports[cam_group_idx], verbose=True)
    sender.send(msg_bytes)
