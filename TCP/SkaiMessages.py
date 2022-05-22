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

class SkaiMsg(ABC):
    """Skai Abstract Base Class for standard messages"""

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


    msg_type = MsgType.UNKNOWN

    @classmethod
    @abstractmethod
    def pack(cls, protobuf):
        raise NotImplementedError

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


class SkaimotMsg(SkaiMsg):
    """SkaiMOT message packing/unpacking/port definitions"""
    msg_type = SkaiMsg.MsgType.SKAIMOT
    proto_msg_class = SkaimotProtoMsg
    port = 6940

    @classmethod
    def pack(cls, protobuf):
        """ 
        packed data format
            msg type id (uint16)
            num of cameras in camera group (uint16)
            [
                timestamp (double)

                number of tracks (uint16)
                tracklist [id, id, id]
                
                number of bboxes (uint16)
                bbox_list [ [ul_x, ul_y, br_x, br_y], ... ] floats
                    (where x and y values are floats from 0 to 1)
                
                number of face embed (uint16)
                face_embed_list[ [512 floats], ...]
                
                number of bbox embed (uint16)
                bbox_embed_list[ [2048 floats], ...]
            ] 
            ... for num cams in camera group

        """
        # header info
        msg_bytes = struct.pack('! H d', MsgType.SKAIMOT.value, timestamp)




class PoseMsg(SkaiMsg):
    """Pose message packing/unpacking/port definitions"""
    msg_type = SkaiMsg.MsgType.POSE
    proto_msg_class = PoseProtoMsg
    port = 6941 # TODO change these to a port range so you can handle multiple camera groups

    @staticmethod
    def set_xy(xy, protobuf):
        protobuf.x, protobuf.y = xy

    @staticmethod
    def set_keypoints(keypoint_list, protobuf):
        PoseMsg.set_xy(keypoint_list[0],  protobuf.nose)
        PoseMsg.set_xy(keypoint_list[1],  protobuf.left_eye)
        PoseMsg.set_xy(keypoint_list[2],  protobuf.right_eye)
        PoseMsg.set_xy(keypoint_list[3],  protobuf.left_ear)
        PoseMsg.set_xy(keypoint_list[4],  protobuf.right_ear)
        PoseMsg.set_xy(keypoint_list[5],  protobuf.left_shoulder)
        PoseMsg.set_xy(keypoint_list[6],  protobuf.right_shoulder)
        PoseMsg.set_xy(keypoint_list[7],  protobuf.left_elbow)
        PoseMsg.set_xy(keypoint_list[8],  protobuf.right_elbow)
        PoseMsg.set_xy(keypoint_list[9],  protobuf.left_wrist)
        PoseMsg.set_xy(keypoint_list[10], protobuf.right_wrist)
        PoseMsg.set_xy(keypoint_list[11], protobuf.left_hip)
        PoseMsg.set_xy(keypoint_list[12], protobuf.right_hip)
        PoseMsg.set_xy(keypoint_list[13], protobuf.left_knee)
        PoseMsg.set_xy(keypoint_list[14], protobuf.right_knee)
        PoseMsg.set_xy(keypoint_list[15], protobuf.left_ankle)
        PoseMsg.set_xy(keypoint_list[16], protobuf.right_ankle)
        PoseMsg.set_xy(keypoint_list[17], protobuf.neck)        

    @classmethod
    def pack(cls, protobuf):
        print(f'packing {cls.__name__}')
        """packs using protobufs for inter-language usage
        """
        # message type id num 
        msg_bytes = struct.pack('! H', cls.msg_type.value)

        # append protobuf message
        msg_bytes += protobuf.SerializeToString()  # (actually serializes to bytes)
    
        # return bytes
        return msg_bytes



class FeetPosMsg(SkaiMsg):

    msg_type = SkaiMsg.MsgType.FEETPOS
    proto_msg_class = FeetPosProtoMsg
    port = 6969

    @staticmethod
    def set_xyz(xyz, protobuf):
        protobuf.x, protobuf.y, protobuf.z = xyz
    
    @classmethod
    def pack(cls, protobuf):
        print(f'packing {cls.__name__}')
         # message type id num 
        msg_bytes = struct.pack('! H', cls.msg_type.value)
        # append protobuf message
        msg_bytes += protobuf.SerializeToString()  # (actually serializes to bytes)
        # return bytes
        return msg_bytes
    


def unpack_and_print_cam_id_and_timestamp_per_frame(msg_bytes):
    # unpack message
    msg_type, msg = SkaiMsg.unpack(msg_bytes)
    print(f'got {msg_type}, data: {msg}')
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

    cam_identifier_macs = ['00:10:FA:66:42:11', '00:10:FA:66:42:21', '00:10:FA:66:42:31', '00:10:FA:66:42:41', '00:10:FA:66:42:51']
    cam_identifier_nums = SkaiMsg.convert_mac_addr_to_camera_identifier_number(cam_identifier_macs)

    # example timestamp (feel free to reuse everywhere for testing)
    ts = int(time.time() * 1e9)  # integer version of double * 1e9
    
    """ test skaimot msg """
    if test_skaimot:
        pass
        # # pack message
        # ts = time.time()  # use double not float
        # trackid_list = [42, 69]
        # bbox_list = [[0.2, 0.21, 0.4, 0.42], [0.2, 0.21, 0.4, 0.42]]
        # face_embed_list = [np.arange(512).tolist(), np.arange(512).tolist()]
        # msg_bytes = SkaimotMsg.pack(ts, trackid_list, bbox_list, face_embed_list)

        # # unpack message
        # ret_id, ret_stamp, ret_tracklist, ret_bboxlist, ret_face_embed_list, ret_bbox_embed_list = SkaiMsg.unpack(
        #     msg_bytes)
        # print(ret_id, ret_stamp, ret_tracklist, ret_bboxlist, ret_face_embed_list,
        #       ret_bbox_embed_list)
        
        # test unpacking
        unpack_and_print_cam_id_and_timestamp_per_frame(msg_bytes)
        
    """ test pose msg """
    if test_pose:
    
        # keypoint x y coordinates scaled between 0 and 1 for width and height
        keypoints = [
            [0.01, 0.01], [0.02, 0.02], [0.03, 0.03], [0.04, 0.04], [0.05, 0.05], [0.06, 0.06],
            [0.07, 0.07], [0.08, 0.08], [0.09, 0.09], [0.10, 0.10], [0.11, 0.11], [0.12, 0.12],
            [0.13, 0.13], [0.14, 0.14], [0.15, 0.15], [0.16, 0.16], [0.17, 0.17], [0.18, 0.18]
        ]
        
        # create protobuf message
        msg = PoseProtoMsg()
        for cam_idx in range(num_cams):
            camframe = msg.camera_frames.add()
            camframe.camera_id = cam_identifier_nums[cam_idx]
            camframe.timestamp = ts # reuse for testing
            people = camframe.people_in_frame.add()
            for person_idx in range(num_people):
                person = people.keypoints.add()
                PoseMsg.set_keypoints(keypoints, person) # reuse for testing
        msg_bytes = PoseMsg.pack(msg) # adds message type id in front 
        
        # test unpacking
        unpack_and_print_cam_id_and_timestamp_per_frame(msg_bytes)

    """ test feet pos msg """
    if test_feetpos:
        foot_pos = [420, 69.2, 0] # xyz float meters
        msg = FeetPosProtoMsg()
        for cam_idx in range(num_cams):
            camframe = msg.camera_frames.add()
            camframe.camera_id = cam_identifier_nums[cam_idx]
            camframe.timestamp = ts # reuse for testing
            people = camframe.people_in_frame.add()
            for person_idx in range(num_people):
                person = people.feetpos.add()
                FeetPosMsg.set_xyz(foot_pos, person) # reuse same foot_pos for testing
        msg_bytes = FeetPosMsg.pack(msg) # add message type id in front 

        # test unpacking
        unpack_and_print_cam_id_and_timestamp_per_frame(msg_bytes)