from skaimsginterface.skaimessages import *

if __name__=='__main__':
        
    # testing 2 people in frame, 5 cameras in camera group
    num_people = 2
    num_cams = 5

    # example skaimot track ids 
    # repeated across cams for testing
    trackid_list = [42, 69, 113, 1244, 333] 

    # example camera id numbers
    cam_identifier_macs = ['00:10:FA:66:42:11', '00:10:FA:66:42:21', '00:10:FA:66:42:31', '00:10:FA:66:42:41', '00:10:FA:66:42:51']
    cam_identifier_nums = SkaiMsg.convert_mac_addr_to_camera_identifier_number(cam_identifier_macs)

    # example timestamp (feel free to reuse everywhere for testing)
    ts = int(time.time() * 1e9)  # integer version of double * 1e9
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

    # unpack message
    msg_type, msg = SkaiMsg.unpack(msg_bytes)
    print(f'got msg type {msg_type}, data: {msg}')
    for frame_data in msg.camera_frames:
        # print camera id and timestamp
        print(f'cam id: {frame_data.camera_id}, timestamp: {frame_data.timestamp}')
