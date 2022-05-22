#!/usr/bin/python3

import struct
import time
from datetime import datetime
import numpy as np

from enum import Enum

from abc import ABC, abstractmethod

# import protobuf messages
from protobuf_messages.generated_msgs.python.SkaimotProtoMsg_pb2 import SkaimotProtoMsg
from protobuf_messages.generated_msgs.python.PoseProtoMsg_pb2 import PoseProtoMsg
from protobuf_messages.generated_msgs.python.FeetPosProtoMsg_pb2 import FeetPosProtoMsg

import code

class SkaiMsg(ABC):
    """Skai Abstract Base Class for standard messages"""

    @classmethod
    def new_msg(cls):
        """creates a new instance of the message class's protobuf class

        Returns:
            protobuf class of appropriate message type
        """
        return cls.proto_msg_class()

    class MsgType(Enum):
        UNKNOWN = 0
        SKAIMOT = 1
        POSE = 2
        FEETPOS = 3

        @classmethod
        def get_class_from_id(cls, id):
            if id == cls.SKAIMOT.value:
                return SkaimotMsg
            elif id == cls.POSE.value:
                return PoseMsg
            elif id == cls.FEETPOS.value:
                return FeetPosMsg
            else:
                return None

    @classmethod
    def pack(cls, protobuf_msg):
        print(f'packing {cls.__name__} protobuf message')
        msg_bytes = struct.pack('! H', cls.msg_type.value)
        msg_bytes += protobuf_msg.SerializeToString() 
        return msg_bytes

    @classmethod
    def unpack(cls, msg_bytes):
        """unpacks message after decoding message id and forwarding to appropriate function

        Args:
            msg_bytes (bytes): bytes from message payload

        Returns:
            SkaiMsg.MsgType enum
            ProtobufMsg
        """
        msg_type_id = cls.unpack_msgid(msg_bytes)
        classRef = cls.MsgType.get_class_from_id(msg_type_id)
        if classRef is not None:
            print(f'unpacking {classRef.__name__}')
            msg = classRef.proto_msg_class()
            msg.ParseFromString(msg_bytes[2:]) # unpack after the 2 msg type bytes
            return classRef.msg_type, msg
        else:
            print('msg id not found')
            return None, None

    @staticmethod
    def unpack_msgid(msg_bytes):
        return struct.unpack('! H', msg_bytes[:2])[0]

    @staticmethod
    def unpack_timestamp(msg_bytes):
        return struct.unpack('! d', msg_bytes[2:10])[0]

    @staticmethod
    def printTimestamp(timestamp):
        print(datetime.fromtimestamp(timestamp))

    @staticmethod    
    def convert_mac_addr_to_camera_identifier_number(string_or_list):
        if isinstance(string_or_list, list):
            return [SkaiMsg.convert_mac_addr_to_camera_identifier_number(string) for string in string_or_list]
        elif isinstance(string_or_list, str):
            # remove ':' and '-' chars from hex string
            string_or_list = string_or_list.replace(':','')
            string_or_list = string_or_list.replace('-','')
            return int(string_or_list, 16)
        else:
            print(f'unsupported type for conversion: {type(string_or_list)}')

    
    """ required class variables in subclasses """
    
    @property
    def msg_type(self):
        """ required variable in subclass """
        raise NotImplementedError

    @property
    def proto_msg_class(self):
        """ required variable in subclass """
        raise NotImplementedError


class SkaimotMsg(SkaiMsg):
    """SkaiMOT message packing/unpacking/port definitions"""
    msg_type = SkaiMsg.MsgType.SKAIMOT
    proto_msg_class = SkaimotProtoMsg
    port = 6940

    """ person metadata setting helper functions """
    
    @staticmethod
    def set_bbox(person, tlbr):
        box = person.box
        box.topleft.x, box.topleft.y, box.botright.x, box.botright.y = tlbr

    @staticmethod
    def set_face_embed(person, face_embed):
        person.face_embedding.vals.extend(face_embed)

    @staticmethod
    def set_bbox_embed(person, bbox_embed):
        person.bbox_embedding.vals.extend(bbox_embed)

class PoseMsg(SkaiMsg):
    """Pose message packing/unpacking/port definitions"""
    msg_type = SkaiMsg.MsgType.POSE
    proto_msg_class = PoseProtoMsg
    port = 6941 # TODO change these to a port range so you can handle multiple camera groups

    """ person metadata setting helper functions """

    @staticmethod
    def set_keypoints(person, keypoint_list):
        # set each keypoint xy value
        PoseMsg.set_xy(person.nose, keypoint_list[0])
        PoseMsg.set_xy(person.left_eye, keypoint_list[1])
        PoseMsg.set_xy(person.right_eye, keypoint_list[2])
        PoseMsg.set_xy(person.left_ear, keypoint_list[3])
        PoseMsg.set_xy(person.right_ear, keypoint_list[4])
        PoseMsg.set_xy(person.left_shoulder, keypoint_list[5])
        PoseMsg.set_xy(person.right_shoulder, keypoint_list[6])
        PoseMsg.set_xy(person.left_elbow, keypoint_list[7])
        PoseMsg.set_xy(person.right_elbow, keypoint_list[8])
        PoseMsg.set_xy(person.left_wrist, keypoint_list[9])
        PoseMsg.set_xy(person.right_wrist, keypoint_list[10])
        PoseMsg.set_xy(person.left_hip, keypoint_list[11])
        PoseMsg.set_xy(person.right_hip, keypoint_list[12])
        PoseMsg.set_xy(person.left_knee, keypoint_list[13])
        PoseMsg.set_xy(person.right_knee, keypoint_list[14])
        PoseMsg.set_xy(person.left_ankle, keypoint_list[15])
        PoseMsg.set_xy(person.right_ankle, keypoint_list[16])
        PoseMsg.set_xy(person.neck, keypoint_list[17])        

    @staticmethod
    def set_xy(keypoint, xy):
        keypoint.x, keypoint.y = xy


class FeetPosMsg(SkaiMsg):

    msg_type = SkaiMsg.MsgType.FEETPOS
    proto_msg_class = FeetPosProtoMsg
    port = 6969
    
    """ person metadata setting helper functions """

    @staticmethod
    def set_feet_pos(person, xyz):
        feetpos = person.feet_position
        feetpos.x, feetpos.y, feetpos.z = xyz
    

def unpack_and_print_cam_id_and_timestamp_per_frame(msg_bytes):
    # unpack message
    msg_type, msg = SkaiMsg.unpack(msg_bytes)
    print(f'got msg type {msg_type}, data: {msg}')
    for frame_data in msg.camera_frames:
        # print camera id and timestamp
        print(f'cam id: {frame_data.camera_id}, timestamp: {frame_data.timestamp}')
    

if __name__ == '__main__':
    
    test_skaimot = False
    test_pose = False
    test_feetpos = True
    
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