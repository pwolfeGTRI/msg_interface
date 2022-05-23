from skaimsginterface.tcp.SkaiMessages import *

if __name__=='__main__':
    example_feetpos = [420, 69.2, 0] # xyz float meters to be reused per person

    # create new protobuf message and load with values
    msg = FeetPosMsg.new_msg()
    for cam_idx in range(num_cams):
        
        # add new camera frame to the message & set id + timestamp
        camframe = msg.camera_frames.add() 
        camframe.camera_id = cam_identifier_nums[cam_idx]
        camframe.timestamp = ts # reuse for testing
        
        # add people to frame
        for person_idx in range(num_people):
            person = camframe.people_in_frame.add()
            # set person's metadata
            person.id = trackid_list[person_idx]
            FeetPosMsg.set_feet_pos(person, example_feetpos) # reuse same foot_pos for testing

    # pack for sending across network
    msg_bytes = FeetPosMsg.pack(msg) # add message type id in front 
