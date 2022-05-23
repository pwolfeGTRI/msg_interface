from skaimsginterface.skaimessages import *

def unpack_and_print_cam_id_and_timestamp_per_frame(msg_bytes):
    # unpack message
    msg_type, msg = SkaiMsg.unpack(msg_bytes)
    print(f'got msg type {msg_type}, data: {msg}')
    for frame_data in msg.camera_frames:
        # print camera id and timestamp
        print(f'cam id: {frame_data.camera_id}, timestamp: {frame_data.timestamp}')
    

def test_tcp_messages(test_skaimot=True, test_pose=True, test_feetpos=True):
    #### TCP Message packing/unpacking testing ####
    
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
    
    """ test skaimot msg """
    if test_skaimot:
        
        # example bounding boxes & face embeddings & bbox embedding per person
        bbox = [0.2, 0.21, 0.4, 0.42]
        face_embed = np.arange(512).tolist()
        bbox_embed = np.arange(2048).tolist()

        # create new protobuf message and load with values
        msg = SkaimotMsg.new_msg()
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
                SkaimotMsg.set_bbox(person, bbox)
                SkaimotMsg.set_face_embed(person, face_embed)
                SkaimotMsg.set_bbox_embed(person, bbox_embed)
        
        # pack for sending across network
        msg_bytes = SkaimotMsg.pack(msg)

        # test unpacking & printing individual camera data
        unpack_and_print_cam_id_and_timestamp_per_frame(msg_bytes)
        
    """ test pose msg """
    if test_pose:
    
        # keypoint x y coordinates scaled between 0 and 1 for width and height
        example_keypoints = [
            [0.01, 0.01], [0.02, 0.02], [0.03, 0.03], [0.04, 0.04], [0.05, 0.05], [0.06, 0.06],
            [0.07, 0.07], [0.08, 0.08], [0.09, 0.09], [0.10, 0.10], [0.11, 0.11], [0.12, 0.12],
            [0.13, 0.13], [0.14, 0.14], [0.15, 0.15], [0.16, 0.16], [0.17, 0.17], [0.18, 0.18]
        ]
        
        # create new protobuf message and load with values
        msg = PoseMsg.new_msg()
        for cam_idx in range(num_cams):
            
            # add new camera frame to the message & set id + timestamp
            camframe = msg.camera_frames.add()
            camframe.camera_id = cam_identifier_nums[cam_idx]
            camframe.timestamp = ts # reuse for testing
            
            # add people to frame
            for person_idx in range(num_people):
                person = camframe.people_in_frame.add()
                # set person's metadata
                PoseMsg.set_keypoints(person, example_keypoints) # reuse for testing

        # pack for sending across network
        msg_bytes = PoseMsg.pack(msg) # adds message type id in front 
        
        # test unpacking & printing individual camera data
        unpack_and_print_cam_id_and_timestamp_per_frame(msg_bytes)

    """ test feet pos msg """
    if test_feetpos:
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

        # test unpacking & printing individual camera data
        unpack_and_print_cam_id_and_timestamp_per_frame(msg_bytes)

        # test zero z value of feet position of first person in first camera frame
        msg_type, msg = SkaiMsg.unpack(msg_bytes)
        print(f'is z value 0?: {msg.camera_frames[0].people_in_frame[0].feet_position.z}')

def test_database_messages(test_localtrack=True, test_globaltrack=True):
    # TODO setup later once database has been setup
    pass

if __name__ == '__main__':
    test_tcp_messages(test_skaimot=True, test_pose=True, test_feetpos=True)
    # test_database_messages(test_localtrack=True, test_globaltrack=True)
    