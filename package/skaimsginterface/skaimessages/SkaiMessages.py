#!/usr/bin/python3

import struct
import time
from datetime import datetime
import numpy as np
from enum import Enum
from abc import ABC, abstractmethod

from .generated_python import *

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
        LOCALTRACK = 4
        GLOBALTRACK = 5
        ACTION = 6

        @classmethod
        def get_class_from_id(cls, id):
            if id == cls.SKAIMOT.value:
                return SkaimotMsg
            elif id == cls.POSE.value:
                return PoseMsg
            elif id == cls.FEETPOS.value:
                return FeetPosMsg
            elif id == cls.LOCALTRACK.value:
                return LocalTrackMsg
            elif id == cls.GLOBALTRACK.value:
                return GlobalTrackMsg
            elif id == cls.ACTION.value:
                return ActionMsg
            else:
                return None

    @classmethod
    def pack(cls, protobuf_msg, verbose=False):
        if verbose:
            print(f'packing {cls.__name__} protobuf message')
        msg_bytes = struct.pack('! H', cls.msg_type.value)
        msg_bytes += protobuf_msg.SerializeToString() 
        return msg_bytes

    @classmethod
    def unpack(cls, msg_bytes, verbose=False):
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
            if verbose:
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

    @classmethod
    def getMessageTypeName(cls, msg_bytes):
        msg_type_id = cls.unpack_msgid(msg_bytes)
        classRef = cls.MsgType.get_class_from_id(msg_type_id)
        if classRef is not None:
            return classRef.__name__
        else:
            print('msg id not found')
            return None

    @staticmethod
    def printTimestamp(timestamp):
        print(datetime.fromtimestamp(timestamp / 1e9))

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
    ports = [6940] # increase to handle more camera groups

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
    ports = [6941] # increase to handle more camera groups

    """ person metadata setting helper functions """

    @classmethod
    def set_keypoints(cls, person, keypoint_list):
        # set each keypoint xy value
        cls.set_xy(person.nose, keypoint_list[0])
        cls.set_xy(person.left_eye, keypoint_list[1])
        cls.set_xy(person.right_eye, keypoint_list[2])
        cls.set_xy(person.left_ear, keypoint_list[3])
        cls.set_xy(person.right_ear, keypoint_list[4])
        cls.set_xy(person.left_shoulder, keypoint_list[5])
        cls.set_xy(person.right_shoulder, keypoint_list[6])
        cls.set_xy(person.left_elbow, keypoint_list[7])
        cls.set_xy(person.right_elbow, keypoint_list[8])
        cls.set_xy(person.left_wrist, keypoint_list[9])
        cls.set_xy(person.right_wrist, keypoint_list[10])
        cls.set_xy(person.left_hip, keypoint_list[11])
        cls.set_xy(person.right_hip, keypoint_list[12])
        cls.set_xy(person.left_knee, keypoint_list[13])
        cls.set_xy(person.right_knee, keypoint_list[14])
        cls.set_xy(person.left_ankle, keypoint_list[15])
        cls.set_xy(person.right_ankle, keypoint_list[16])
        cls.set_xy(person.neck, keypoint_list[17])        

    @staticmethod
    def set_xy(keypoint, xy):
        keypoint.x, keypoint.y = xy

class FeetPosMsg(SkaiMsg):

    msg_type = SkaiMsg.MsgType.FEETPOS
    proto_msg_class = FeetPosProtoMsg
    ports = [6969] # increase to handle more camera groups
    
    """ person metadata setting helper functions """

    @staticmethod
    def set_feet_pos(person, xyz):
        feetpos = person.feet_position
        feetpos.x, feetpos.y, feetpos.z = xyz
    
class LocalTrackMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.LOCALTRACK
    proto_msg_class = LocalTrackProtoMsg
    ports = [7000] # increase to handle more camera groups

    @staticmethod
    def copy_bbox(localbbox, skaimotPerson):
        box = skaimotPerson.box
        localbbox.topleft.x = box.topleft.x
        localbbox.topleft.y = box.topleft.y
        localbbox.botright.x = box.botright.x
        localbbox.botright.y = box.botright.y

    @classmethod
    def copy_pose(cls, localpose, posePerson):
        pnts = localpose.keypoints
        cls.copy_xy(pnts.nose, posePerson.nose)
        cls.copy_xy(pnts.left_eye, posePerson.left_eye)
        cls.copy_xy(pnts.right_eye, posePerson.right_eye)
        cls.copy_xy(pnts.left_ear, posePerson.left_ear)
        cls.copy_xy(pnts.right_ear, posePerson.right_ear)
        cls.copy_xy(pnts.left_shoulder, posePerson.left_shoulder)
        cls.copy_xy(pnts.right_shoulder, posePerson.right_shoulder)
        cls.copy_xy(pnts.left_elbow, posePerson.left_elbow)
        cls.copy_xy(pnts.right_elbow, posePerson.right_elbow)
        cls.copy_xy(pnts.left_wrist, posePerson.left_wrist)
        cls.copy_xy(pnts.right_wrist, posePerson.right_wrist)
        cls.copy_xy(pnts.left_hip, posePerson.left_hip)
        cls.copy_xy(pnts.right_hip, posePerson.right_hip)
        cls.copy_xy(pnts.left_knee, posePerson.left_knee)
        cls.copy_xy(pnts.right_knee, posePerson.right_knee)
        cls.copy_xy(pnts.left_ankle, posePerson.left_ankle)
        cls.copy_xy(pnts.right_ankle, posePerson.right_ankle)
        cls.copy_xy(pnts.neck, posePerson.neck)

    @staticmethod
    def copy_xy(localxy, xy):
        localxy.x, localxy.y = xy.x, xy.y

    @staticmethod
    def copy_feet(feet, feetperson):
        feetpos = feetperson.feet_position
        feet.x, feet.y, feet.z = feetpos.x, feetpos.y, feetpos.z

    @staticmethod
    def copy_faceembed(faceembed, skaimotperson):
        faceembed.vals.extend(skaimotperson.face_embedding.vals)
    
    @staticmethod
    def copy_bboxembed(bboxembed, skaimotperson):
        bboxembed.vals.extend(skaimotperson.bbox_embedding.vals)

    @staticmethod
    def copy_action(action, actionperson):
        pass

class GlobalTrackMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.GLOBALTRACK
    proto_msg_class = GlobalTrackProtoMsg
    ports = [7020] # increase to handle more camera groups

class ActionMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.ACTION
    proto_msg_class = ActionProtoMsg
    ports = [7040]

