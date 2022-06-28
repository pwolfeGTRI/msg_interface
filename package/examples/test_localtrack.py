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
    example_skaimotmsg = create_example_skaimotmsg()
    example_posemsg = create_example_posemsg()
    example_feetposmsg = create_example_feetposmsg()
    example_actionmsg = create_example_actionmsg()

    # grab an example frame and person from each example message for example
    # This super simple exmaple assumes that
    # all camera id numbers lists are same across message types
    # more advanced logic needed in real one
    camera_idx = 0 
    person_idx = 0
    action_idx = 0
    example_max_list_length = 3

    skaimotframe = example_skaimotmsg.camera_frames[camera_idx]
    skaimotperson = skaimotframe.people_in_frame[person_idx]

    poseframe = example_posemsg.camera_frames[camera_idx]
    poseperson = poseframe.people_in_frame[person_idx]
    
    feetframe = example_feetposmsg.camera_frames[camera_idx]
    feetperson = feetframe.people_in_frame[person_idx]

    actionframe = example_actionmsg.camera_frames[camera_idx]
    # example_action = actionframe.actions_in_frame[action_idx]

    # use to populate local track message
    msg = LocalTrackMsg.new_msg()
    msg.id = skaimotperson.id
    msg.active = True
    # tally up a local circular buffer (collections.deque) to choose
    # SkaiMsg.CLASSIFICATION.EMPLOYEE vs SkaiMsg.CLASSIFICATION.CUSTOMER
    # in this example we'll just copy directly
    msg.classification = skaimotperson.classification
    msg.camera_id = skaimotframe.camera_id

    # copy over from skaimot msg if first time (default value is 0)
    if msg.time_discovered == 0:
        msg.time_discovered = skaimotframe.timestamp
       
    # add a new box to list and
    # populate local track bbox from skaimot person's box
    bbox = SkaiMsg.add_to_list_w_maxlength(msg.bbox_list)
    bbox.timestamp = skaimotframe.timestamp
    LocalTrackMsg.copy_bbox(bbox, skaimotperson)

    # populate face & bbox embeddings from skaimot person
    # (goes from 351 bytes to 10623 bytes per msg with these)
    faceembed = SkaiMsg.add_to_list_w_maxlength(msg.face_embed_list)
    faceembed.timestamp = skaimotframe.timestamp
    LocalTrackMsg.copy_faceembed(faceembed, skaimotperson)

    bboxembed = SkaiMsg.add_to_list_w_maxlength(msg.bbox_embed_list)
    bboxembed.timestamp = skaimotframe.timestamp
    LocalTrackMsg.copy_bboxembed(bboxembed, skaimotperson)

    # add new pose and populate from pose person's keypoints
    pose = SkaiMsg.add_to_list_w_maxlength(msg.pose_list)
    pose.timestamp = poseframe.timestamp
    LocalTrackMsg.copy_pose(pose, poseperson)

    # add feet position
    feet = SkaiMsg.add_to_list_w_maxlength(msg.feet_position_list)
    feet.timestamp = feetframe.timestamp
    LocalTrackMsg.copy_feet(feet, feetperson)

    # TODO add action example
    # action = SkaiMsg.add_to_list_w_maxlength(msg.action_list)
    # action.timestamp = actionframe.timestamp
    # action.action = example_action

    # print message
    # print(msg)
       
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
