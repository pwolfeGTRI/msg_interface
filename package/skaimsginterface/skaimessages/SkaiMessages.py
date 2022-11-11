#!/usr/bin/python3

import struct
import time
from datetime import datetime
import numpy as np
from enum import Enum
from abc import ABC, abstractmethod

from skaiproto.ActionProtoMsg_pb2 import ActionProtoMsg
from skaiproto.FeetPosProtoMsg_pb2 import FeetPosProtoMsg
from skaiproto.GlobalTrackProtoMsg_pb2 import GlobalTrackProtoMsg
from skaiproto.LocalTrackProtoMsg_pb2 import LocalTrackProtoMsg
from skaiproto.PoseProtoMsg_pb2 import PoseProtoMsg
from skaiproto.SkaimotProtoMsg_pb2 import SkaimotProtoMsg
from skaiproto.SkaiEventProtoMsg_pb2 import SkaiEventProtoMsg
from skaiproto.SkaiboxMsgsProtoMsg_pb2 import SkaiboxDealershipMsgProtoMsg, SkaiboxCameraCalibrationMsgProtoMsg, SkaiboxCameraGroupMsgProtoMsg, SkaiboxDatabaseCloudMsgProtoMsg
from skaiproto.InteractionProtoMsg_pb2 import TracksInDealershipProtoMsg, InteractionInDealershipProtoMsg
from skaiproto.VehicleProtoMsg_pb2 import VehicleProtoMsg, VehicleSpotMonitorProtoMsg
from skaiproto.SkaiGooeyProtoMsg_pb2 import SkaiGooeyProtoMsg
from skaiproto import *

class SkaiMsg(ABC):
    """Skai Abstract Base Class for standard messages"""

    @classmethod
    def new_msg(cls):
        """creates a new instance of the message class's protobuf class

        Returns:
            protobuf class of appropriate message type
        """
        return cls.proto_msg_class()

    # pointer to enums from protobuf
    CLASSIFICATION = SkaimotProtoMsg_pb2.Classification
    ACTION = ActionProtoMsg_pb2.ActionType
    SKAIEVENT = SkaiEventProtoMsg_pb2.SkaiEvent
    SKAIBOX_COMMAND = SkaiboxMsgsProtoMsg_pb2.SkaiboxCommand
    SKAIBOX_RESPONSE = SkaiboxMsgsProtoMsg_pb2.SkaiboxResponse

    # add to list check max length
    @classmethod
    def add_to_list_w_maxlength(cls, protobuflist, max_length=100):
        msg = protobuflist.add()
        cls.limit_list_length(protobuflist, max_length)
        return msg

    # limit list to a max length
    @staticmethod
    def limit_list_length(protobuflist, max_length=100):
        if len(protobuflist) > max_length:
            del protobuflist[0]

    class MsgType(Enum):
        UNKNOWN = 0
        SKAIMOT = 1
        POSE = 2
        FEETPOS = 3
        LOCALTRACK = 4
        GLOBALTRACK = 5
        ACTION = 6
        SKAIBOX_DEALERSHIP = 7
        SKAIBOX_CAMERACALIBRATION = 8
        SKAIBOX_CAMERAGROUP = 9
        SKAIBOX_DATABASECLOUD = 10
        TRACKS_IN_DEALERSHIP = 11
        INTERACTION_IN_DEALERSHIP = 12
        VEHICLE = 13
        VEHICLE_SPOT_MONITOR = 14
        SKAI_EVENT = 15
        SKAI_GOOEY = 16

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
            elif id == cls.SKAIBOX_DEALERSHIP.value:
                return SkaiboxDealershipMsg
            elif id == cls.SKAIBOX_CAMERACALIBRATION.value:
                return SkaiboxCameraCalibrationMsg
            elif id == cls.SKAIBOX_CAMERAGROUP.value:
                return SkaiboxCameraGroupMsg
            elif id == cls.SKAIBOX_DATABASECLOUD.value:
                return SkaiboxDatabaseCloudMsg
            elif id == cls.TRACKS_IN_DEALERSHIP.value:
                return TracksInDealershipMsg
            elif id == cls.INTERACTION_IN_DEALERSHIP.value:
                return InteractionInDealershipMsg
            elif id == cls.VEHICLE.value:
                return VehicleMsg
            elif id == cls.VEHICLE_SPOT_MONITOR.value:
                return VehicleSpotMonitorMsg
            elif id == cls.SKAI_EVENT.value:
                return SkaiEventMsg
            elif id == cls.SKAI_GOOEY.value:
                return SkaiGooeyMsg
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
        try:
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
        except Warning:
            print(f'warning during SkaiMsg unpack!!')
        except Exception as e:
            print(f'[SkaiMsg.unpack Exception]: {e}')
            return None, None

    @staticmethod
    def unpack_msgid(msg_bytes):
        try:
            return struct.unpack('! H', msg_bytes[:2])[0]
        except:
            print(f'could not unpack msg id!')
            return None

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

    
    @staticmethod
    def convert_camera_id_to_mac_addr_string(int_or_list):
        if isinstance(int_or_list, list):
            return [SkaiMsg.convert_camera_id_to_mac_addr_string(num) for num in int_or_list]
        elif isinstance(int_or_list, int):
            hexstr = f'{int_or_list:0>12X}'
            return ':'.join([hexstr[i:i+2] for i in range(0, len(hexstr),2)])
        else:
            print(f'unsupported type for conversion: {type(int_or_list)}')

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
    ports = list(range(6000, 6100))
    pose_ports = list(range(6600, 6700))

    """ person metadata setting helper functions """
    @staticmethod
    def set_bbox(person, tlbr):
        box = person.box
        box.top, box.left, box.bottom, box.right = tlbr

    @staticmethod
    def set_face_embed(person, face_embed, timestamp=None):
        person.face_embedding.vals.extend(face_embed)
        if timestamp:
            person.face_embedding.timestamp = timestamp

    @staticmethod
    def set_bbox_embed(person, bbox_embed, timestamp=None):
        person.bbox_embedding.vals.extend(bbox_embed)
        if timestamp:
            person.bbox_embedding.timestamp = timestamp

class PoseMsg(SkaiMsg):
    """Pose message packing/unpacking/port definitions"""
    msg_type = SkaiMsg.MsgType.POSE
    proto_msg_class = PoseProtoMsg
    ports = list(range(6100, 6200))

    """ person metadata setting helper functions """

    @classmethod
    def set_keypoints(cls, person, keypoint_list, timestamp):
        # set each keypoint xy value
        cls.set_xy(person.keypoints.nose,               keypoint_list[0])
        cls.set_xy(person.keypoints.left_eye_inner,     keypoint_list[1])
        cls.set_xy(person.keypoints.left_eye,           keypoint_list[2])
        cls.set_xy(person.keypoints.left_eye_outer,     keypoint_list[3])
        cls.set_xy(person.keypoints.right_eye_inner,    keypoint_list[4])
        cls.set_xy(person.keypoints.right_eye,          keypoint_list[5])
        cls.set_xy(person.keypoints.right_eye_outer,    keypoint_list[6])
        cls.set_xy(person.keypoints.left_ear,           keypoint_list[7])
        cls.set_xy(person.keypoints.right_ear,          keypoint_list[8])
        cls.set_xy(person.keypoints.mouth_left,         keypoint_list[9])
        cls.set_xy(person.keypoints.mouth_right,        keypoint_list[10])
        cls.set_xy(person.keypoints.left_shoulder,      keypoint_list[11])
        cls.set_xy(person.keypoints.right_shoulder,     keypoint_list[12])
        cls.set_xy(person.keypoints.left_elbow,         keypoint_list[13])
        cls.set_xy(person.keypoints.right_elbow,        keypoint_list[14])
        cls.set_xy(person.keypoints.left_wrist,         keypoint_list[15])
        cls.set_xy(person.keypoints.right_wrist,        keypoint_list[16])
        cls.set_xy(person.keypoints.left_pinky,         keypoint_list[17])
        cls.set_xy(person.keypoints.right_pinky,        keypoint_list[18])
        cls.set_xy(person.keypoints.left_index,         keypoint_list[19])
        cls.set_xy(person.keypoints.right_index,        keypoint_list[20])
        cls.set_xy(person.keypoints.left_thumb,         keypoint_list[21])
        cls.set_xy(person.keypoints.right_thumb,        keypoint_list[22])
        cls.set_xy(person.keypoints.left_hip ,          keypoint_list[23])
        cls.set_xy(person.keypoints.right_hip,          keypoint_list[24])
        cls.set_xy(person.keypoints.left_knee,          keypoint_list[25])
        cls.set_xy(person.keypoints.right_knee,         keypoint_list[26])
        cls.set_xy(person.keypoints.left_ankle,         keypoint_list[27])
        cls.set_xy(person.keypoints.right_ankle,        keypoint_list[28])
        cls.set_xy(person.keypoints.left_heel,          keypoint_list[29])
        cls.set_xy(person.keypoints.right_heel,         keypoint_list[30])
        cls.set_xy(person.keypoints.left_foot_index,    keypoint_list[31])
        cls.set_xy(person.keypoints.right_foot_index,   keypoint_list[32])
        if timestamp:
            person.keypoints.timestamp = timestamp

    @staticmethod
    def set_orientation(person, vector3d, timestamp=None):
        person.orientation.x = vector3d[0]
        person.orientation.y = vector3d[1]
        person.orientation.z = vector3d[2]
        if timestamp:
            person.orientation.timestamp = timestamp

    @staticmethod
    def set_xy(keypoint, xy):
        keypoint.x, keypoint.y = xy

class FeetPosMsg(SkaiMsg):

    msg_type = SkaiMsg.MsgType.FEETPOS
    proto_msg_class = FeetPosProtoMsg
    ports = list(range(6200, 6300))
    
    """ person metadata setting helper functions """

    @staticmethod
    def set_feet_pos(person, xyz, timestamp=None):
        feetpos = person.feet_position
        feetpos.x, feetpos.y, feetpos.z = xyz
        if timestamp:
            feetpos.timestamp = timestamp
    
class LocalTrackMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.LOCALTRACK
    proto_msg_class = LocalTrackProtoMsg
    ports = list(range(6300, 6400))

    @staticmethod
    def copy_bbox(localbbox, skaimotPerson):
        box = skaimotPerson.box
        localbbox.topleft.x = box.topleft.x
        localbbox.topleft.y = box.topleft.y
        localbbox.botright.x = box.botright.x
        localbbox.botright.y = box.botright.y
        localbbox.timestamp = box.timestamp

    @classmethod
    def copy_pose(cls, localpose, posePerson):
        pnts = localpose
        cls.copy_xy(pnts.nose,              posePerson.keypoints.nose            ) 
        cls.copy_xy(pnts.left_eye_inner,    posePerson.keypoints.left_eye_inner  ) 
        cls.copy_xy(pnts.left_eye,          posePerson.keypoints.left_eye        ) 
        cls.copy_xy(pnts.left_eye_outer,    posePerson.keypoints.left_eye_outer  ) 
        cls.copy_xy(pnts.right_eye_inner,   posePerson.keypoints.right_eye_inner ) 
        cls.copy_xy(pnts.right_eye,         posePerson.keypoints.right_eye       ) 
        cls.copy_xy(pnts.right_eye_outer,   posePerson.keypoints.right_eye_outer ) 
        cls.copy_xy(pnts.left_ear,          posePerson.keypoints.left_ear        ) 
        cls.copy_xy(pnts.right_ear,         posePerson.keypoints.right_ear       ) 
        cls.copy_xy(pnts.mouth_left,        posePerson.keypoints.mouth_left      ) 
        cls.copy_xy(pnts.mouth_right,       posePerson.keypoints.mouth_right     ) 
        cls.copy_xy(pnts.left_shoulder,     posePerson.keypoints.left_shoulder   ) 
        cls.copy_xy(pnts.right_shoulder,    posePerson.keypoints.right_shoulder  ) 
        cls.copy_xy(pnts.left_elbow,        posePerson.keypoints.left_elbow      ) 
        cls.copy_xy(pnts.right_elbow,       posePerson.keypoints.right_elbow     ) 
        cls.copy_xy(pnts.left_wrist,        posePerson.keypoints.left_wrist      ) 
        cls.copy_xy(pnts.right_wrist,       posePerson.keypoints.right_wrist     ) 
        cls.copy_xy(pnts.left_pinky,        posePerson.keypoints.left_pinky      ) 
        cls.copy_xy(pnts.right_pinky,       posePerson.keypoints.right_pinky     ) 
        cls.copy_xy(pnts.left_index,        posePerson.keypoints.left_index      ) 
        cls.copy_xy(pnts.right_index,       posePerson.keypoints.right_index     ) 
        cls.copy_xy(pnts.left_thumb,        posePerson.keypoints.left_thumb      ) 
        cls.copy_xy(pnts.right_thumb,       posePerson.keypoints.right_thumb     ) 
        cls.copy_xy(pnts.left_hip ,         posePerson.keypoints.left_hip        ) 
        cls.copy_xy(pnts.right_hip,         posePerson.keypoints.right_hip       ) 
        cls.copy_xy(pnts.left_knee,         posePerson.keypoints.left_knee       ) 
        cls.copy_xy(pnts.right_knee,        posePerson.keypoints.right_knee      ) 
        cls.copy_xy(pnts.left_ankle,        posePerson.keypoints.left_ankle      ) 
        cls.copy_xy(pnts.right_ankle,       posePerson.keypoints.right_ankle     ) 
        cls.copy_xy(pnts.left_heel,         posePerson.keypoints.left_heel       ) 
        cls.copy_xy(pnts.right_heel,        posePerson.keypoints.right_heel      ) 
        cls.copy_xy(pnts.left_foot_index,   posePerson.keypoints.left_foot_index ) 
        cls.copy_xy(pnts.right_foot_index,  posePerson.keypoints.right_foot_index)
        pnts.timestamp = posePerson.keypoints.timestamp
        
    @staticmethod
    def copy_orientation(orientation, posePerson):
        orientation.x = posePerson.orientation.x
        orientation.y = posePerson.orientation.y
        orientation.z = posePerson.orientation.z
        orientation.timestamp = posePerson.orientation.timestamp

    @staticmethod
    def copy_xy(localxy, xy):
        localxy.x, localxy.y = xy.x, xy.y

    @staticmethod
    def copy_feet(feet, feetperson):
        feetpos = feetperson.feet_position
        feet.x, feet.y, feet.z = feetpos.x, feetpos.y, feetpos.z
        feet.timestamp = feetpos.timestamp

    @staticmethod
    def copy_faceembed(faceembed, skaimotperson):
        faceembed.vals.extend(skaimotperson.face_embedding.vals)
        faceembed.timestamp = skaimotperson.face_embedding.timestamp
    
    @staticmethod
    def copy_bboxembed(bboxembed, skaimotperson):
        bboxembed.vals.extend(skaimotperson.bbox_embedding.vals)
        bboxembed.timestamp = skaimotperson.bbox_embedding.timestamp

    @staticmethod
    def copy_action(action, actionperson):
        pass

class GlobalTrackMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.GLOBALTRACK
    proto_msg_class = GlobalTrackProtoMsg
    ports = list(range(6400, 6500))

    @staticmethod
    def copy_tlbr_box_to_global_bbox(tlbr_box, global_bbox):
        global_bbox.top = tlbr_box.top
        global_bbox.left = tlbr_box.left
        global_bbox.bottom = tlbr_box.bottom
        global_bbox.right = tlbr_box.right

class ActionMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.ACTION
    proto_msg_class = ActionProtoMsg
    ports = list(range(6500, 6600))

class SkaiboxDealershipMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.SKAIBOX_DEALERSHIP
    proto_msg_class = SkaiboxDealershipMsgProtoMsg
    ports_command = list(range(7000, 7100))     # ports to send/recieve commands 
    ports_response = list(range(7100, 7200))    # ports to send/recieve responses

class SkaiboxCameraCalibrationMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.SKAIBOX_CAMERACALIBRATION
    proto_msg_class = SkaiboxCameraCalibrationMsgProtoMsg
    ports_command = list(range(7000, 7100))     # ports to send/recieve commands 
    ports_response = list(range(7100, 7200))    # ports to send/recieve responses

class SkaiboxCameraGroupMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.SKAIBOX_CAMERAGROUP
    proto_msg_class = SkaiboxCameraGroupMsgProtoMsg
    ports_command = list(range(7000, 7100))     # ports to send/recieve commands 
    ports_response = list(range(7100, 7200))    # ports to send/recieve responses

class SkaiboxDatabaseCloudMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.SKAIBOX_DATABASECLOUD
    proto_msg_class = SkaiboxDatabaseCloudMsgProtoMsg
    ports_command = list(range(7000, 7100))     # ports to send/recieve commands 
    ports_response = list(range(7100, 7200))    # ports to send/recieve responses

class TracksInDealershipMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.TRACKS_IN_DEALERSHIP
    proto_msg_class = TracksInDealershipProtoMsg
    ports = list(range(7310, 7320)) # only few per dealership needed

class InteractionInDealershipMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.INTERACTION_IN_DEALERSHIP
    proto_msg_class = InteractionInDealershipProtoMsg
    ports = list(range(7320, 7330)) # only few per dealership needed

class VehicleMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.VEHICLE
    proto_msg_class = VehicleProtoMsg
    ports = list(range(6800, 6900)) 
    vehicle2interacts_ports = list(range(7500,7600))

    @staticmethod
    def set_box_from_list(box, tlbr_list):
        box.top, box.left, box.bottom, box.right = tlbr_list

class VehicleSpotMonitorMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.VEHICLE_SPOT_MONITOR
    proto_msg_class = VehicleSpotMonitorProtoMsg
    ports = list(range(6900,7000))

class SkaiEventMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.SKAI_EVENT
    proto_msg_class = SkaiEventProtoMsg
    ports = list(range(7200,7300))

class SkaiGooeyMsg(SkaiMsg):
    msg_type = SkaiMsg.MsgType.SKAI_GOOEY
    proto_msg_class = SkaiGooeyProtoMsg
    # comes from globaltrackhandler to gui 
    ports = list(range(7300,7310)) # only few per dealership needed 
    # event from interaction to gui
    interacts2gooey_ports = list(range(7330, 7340))

if __name__=='__main__':
    pass

    msg = TracksInDealershipMsg.new_msg()
    TracksInDealershipMsg.pack(msg, verbose=True)

    # camera_macs = ['00:10:FA:66:42:11', '00:10:FA:66:42:12', '00:10:FA:66:42:13']
    # print(camera_macs)
    # camera_ids = SkaiMsg.convert_mac_addr_to_camera_identifier_number(camera_macs)
    # print(camera_ids)
    # camera_macs_ret = SkaiMsg.convert_camera_id_to_mac_addr_string(camera_ids)
    # print(camera_macs_ret)