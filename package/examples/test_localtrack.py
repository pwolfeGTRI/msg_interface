#!/usr/bin/python3
from skaimsginterface.skaimessages import *
from test_skaimot import create_example_skaimotmsg
from test_pose import create_example_posemsg
from test_feetpos import create_example_feetposmsg

# import code 
# variables = globals().copy()
# variables.update(locals())
# shell = code.InteractiveConsole(variables)
# shell.interact()



if __name__=='__main__':

    # create example base messages
    example_skaimotmsg = create_example_skaimotmsg()
    example_posemsg = create_example_posemsg()
    example_feetposmsg = create_example_feetposmsg()

    # grab an example frame and person from each example message for example
    camera_frame_idx = 0
    person_idx = 0

    skaimotframe = example_skaimotmsg.camera_frames[camera_frame_idx]
    skaimotperson = skaimotframe.people_in_frame[person_idx]

    poseframe = example_posemsg.camera_frames[camera_frame_idx]
    poseperson = poseframe.people_in_frame[person_idx]
    
    feetframe = example_feetposmsg.camera_frames[camera_frame_idx]
    feetperson = feetframe.people_in_frame[person_idx]

    
    # TODO populate face embed, bbox embed, actions
    # actionframe = None
    # actionperson = None


    # use to populate local track message
    msg = LocalTrackMsg.new_msg()
    msg.id = skaimotperson.id
    
    msg.camera_id = skaimotframe.camera_id
    # copy over from skaimot msg if first time (default value is 0)
    if msg.time_discovered == 0:
        msg.time_discovered = skaimotframe.timestamp
    
    # add a new box to list and
    # populate local track bbox from skaimot person's box
    bbox = msg.bbox_list.add()
    bbox.timestamp = skaimotframe.timestamp
    LocalTrackMsg.copy_bbox(bbox, skaimotperson)
    
    # add new pose and populate from pose person's keypoints
    pose = msg.pose_list.add()
    pose.timestamp = poseframe.timestamp
    LocalTrackMsg.copy_pose(pose, poseperson)

    # add feet position
    feet = msg.feet_position_list.add()
    feet.timestamp = feetframe.timestamp
    LocalTrackMsg.copy_feet(feet, feetperson)

    # add face embed


    # add bbox embed


    # add action


    # print message
    print(msg)

