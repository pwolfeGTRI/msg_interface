#!/usr/bin/python3

import struct
import time
from datetime import datetime
import numpy as np

from enum import Enum

from abc import ABC, abstractmethod

class SkaiMsg(ABC):
    """Skai Abstract Base Class for standard messages"""

    @classmethod
    @abstractmethod
    def unpack(cls, msg_bytes):
        """unpacks message after decoding message id and forwarding to appropriate function

        Args:
            msg_bytes (bytes): bytes from message payload

        Returns:
            list: unpacked data elements
        """
        msgid = SkaiMsg.unpack_msgid(msg_bytes)
        msgClassRef = MsgType.get_class_from_id(msgid)
        if msgClassRef is not None:
            return msgClassRef.unpack(msg_bytes)
        else:
            print('msg id not found')
            return None

    @staticmethod
    def unpack_msgid(msg_bytes):
        return struct.unpack('! H', msg_bytes[:2])[0]

    @staticmethod
    def unpack_timestamp(msg_bytes):
        return struct.unpack('! d', msg_bytes[2:10])[0]

    @staticmethod
    def printTimestamp(timestamp):
        print(datetime.fromtimestamp(timestamp))

class SkaimotMsg(SkaiMsg):
    """SkaiMOT message packing/unpacking/port definitions"""
    port = 6940

    @staticmethod
    def pack(timestamp, trackid_list=[], bbox_list=[], face_embed_list=[], bbox_embed_list=[]):
        """ 
        packed data format
            msgid (uint16)
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

        """
        # header info
        msg_bytes = struct.pack('! H d', MsgType.SKAIMOT.value, timestamp)    
    
        # track id list
        count = len(trackid_list)
        msg_bytes += struct.pack('! H', count)
        if count > 0:
            msg_bytes += struct.pack(f'! {count}I', *trackid_list)
            
        # bbox [ul_x, ul_y, br_x, br_y]
        count = len(bbox_list)
        msg_bytes += struct.pack('! H', count)
        if count > 0:
            for entry in bbox_list:
                msg_bytes += struct.pack('! 4f', *entry)
        
        # face embedding [512 floats]
        count = len(face_embed_list)
        msg_bytes += struct.pack('! H', count)
        if count > 0:
            for entry in face_embed_list:
                msg_bytes += struct.pack('! 512f', *entry)

        # bbox embedding [2048 floats]
        count = len(bbox_embed_list)
        msg_bytes += struct.pack('! H', count)
        if count > 0:
            for entry in face_embed_list:
                msg_bytes += struct.pack('! 2048f', *bbox_embed_list)

        return msg_bytes        

    @classmethod
    def unpack(cls, msg_bytes):
        print(f'unpacking {cls.__name__}')

        # init empty lists
        trackid_list = []
        bbox_list = []
        face_embed_list = []
        bbox_embed_list = []
        
        # get message id and timestamp
        msgid, timestamp = struct.unpack('! H d', msg_bytes[:10])
        idx = 10

        # track id list
        count = struct.unpack('! H', msg_bytes[idx:idx+2])[0]
        idx += 2
        if count > 0:
            trackid_list = struct.unpack(f'! {count}I', msg_bytes[idx:idx+count*4])
            idx += count*4

        # bbox list
        count = struct.unpack('! H', msg_bytes[idx:idx+2])[0]
        idx += 2
        if count > 0:
            element_size = 4
            for i in range(count):
                bbox_list.append( struct.unpack(f'! {element_size}f', msg_bytes[idx:idx+element_size*4]) )
                idx += element_size*4

        # face embed list
        count = struct.unpack('! H', msg_bytes[idx:idx+2])[0]
        idx += 2
        if count > 0:
            element_size = 512
            for i in range(count):
                face_embed_list.append( struct.unpack(f'! {element_size}f', msg_bytes[idx:idx+element_size*4]) )
                idx += element_size*4
        
        # bbox embed list
        count = struct.unpack('! H', msg_bytes[idx:idx+2])[0]
        idx += 2
        if count > 0:
            element_size = 2048
            for i in range(count):
                bbox_embed_list.append( struct.unpack(f'! {element_size}f', msg_bytes[idx:idx+element_size*4]) )
                idx += element_size*4

        return msgid, timestamp, trackid_list, bbox_list, face_embed_list, bbox_embed_list

class PoseMsg(SkaiMsg):
    """Pose message packing/unpacking/port definitions"""
    port = 6941
    
    @staticmethod
    def pack(timestamp, pose_list=[]):
        """packs 

        Args:
            pose_list (list): format: 
            [ [x1 y1 x2 y2 .... x18, y18], ... ]
            (where x and y values are floats from 0 to 1)

        Returns:
            bytes: packed data format is    
                msgid (uint16)
                timestamp (double)
                number of people (uint16)
                pose list of [36 floats]

        """
        # header info 
        msg_bytes = struct.pack('! H d', MsgType.POSE.value, timestamp)

        # pose list
        count = len(pose_list)
        msg_bytes += struct.pack('! H', count)
        if count > 0:
            for entry in pose_list:
                msg_bytes += struct.pack('! 36f', *entry)

        return msg_bytes

    @classmethod
    def unpack(cls, msg_bytes):
        print(f'unpacking {cls.__name__}')

        # init empty lists
        pose_list = []

        # get message id and timestamp
        msgid, timestamp = struct.unpack('! H d', msg_bytes[:10])
        idx = 10

        count = struct.unpack('! H', msg_bytes[idx:idx+2])[0]
        idx += 2
        if count > 0:
            element_size = 36
            for i in range(count):
                pose_list.append( struct.unpack(f'! {element_size}f', msg_bytes[idx:idx+element_size*4]) )
                idx += element_size*4

        return msgid, timestamp, pose_list

class FeetPositionMsg:
    """Feet position message packing/unpacking/port definitions"""
    port = 6942
    
    @classmethod
    def pack(cls, timestamp, feetpos_list):
        """packs feet position message

        Args:
            timestamp (double): epoch time timestamp
            feetpos_list (list): format [x, y, z] float meters

        Returns:
            bytes: packed feet position message bytes
        """
        # header info 
        msg_bytes = struct.pack('! H d', MsgType.FEETPOS.value, timestamp)

        # feet position list
        count = len(feetpos_list)
        msg_bytes += struct.pack('! H', count)
        if count > 0:
            for entry in feetpos_list:
                msg_bytes += struct.pack('! 3f', *entry)

        return msg_bytes

    @classmethod
    def unpack(cls, msg_bytes):
        print(f'unpacking {cls.__name__}')
        
        # init empty list
        feetpos_list = []

        # get message id and timestamp
        msgid, timestamp = struct.unpack('! H d', msg_bytes[:10])
        idx = 10

        count = struct.unpack('! H', msg_bytes[idx:idx+2])[0]
        idx += 2
        if count > 0:
            element_size = 3
            for i in range(count):
                feetpos_list.append( struct.unpack(f'! {element_size}f', msg_bytes[idx:idx+element_size*4]) )
                idx += element_size*4

        return msgid, timestamp, feetpos_list

class MsgType(Enum):
    SKAIMOT = 1
    POSE = 2
    FEETPOS = 3

    @staticmethod
    def get_class_from_id(id):
        if id == MsgType.SKAIMOT.value:
            return SkaimotMsg
        elif id == MsgType.POSE.value:
            return PoseMsg
        elif id == MsgType.FEETPOS.value:
            return FeetPositionMsg
        else:
            return None

if __name__=='__main__':
    # 2 people in frame testing

    """ test skaimot msg """
    # pack message
    ts = time.time() # use double not float
    trackid_list = [42, 69]
    bbox_list = [[0.2, 0.21, 0.4, 0.42], [0.2, 0.21, 0.4, 0.42]]
    face_embed_list = [ np.arange(512).tolist(), np.arange(512).tolist()]
    msg_bytes = SkaimotMsg.pack(ts, trackid_list, bbox_list, face_embed_list)
    
    # unpack message
    ret_id, ret_stamp, ret_tracklist, ret_bboxlist, ret_face_embed_list, ret_bbox_embed_list = SkaiMsg.unpack(msg_bytes)
    print(ret_id, ret_stamp, ret_tracklist, ret_bboxlist, ret_face_embed_list, ret_bbox_embed_list)
            
    """ test pose msg """
    # pack
    num_people = 2
    person_example=[1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13,14,14,15,15,16,16,17,17,18,18]
    pose_list = [person_example for x in range(num_people)]
    msg_bytes=PoseMsg.pack(ts,pose_list)

    # unpack message
    ret_id, ret_stamp, ret_list = SkaiMsg.unpack(msg_bytes)
    print(ret_id, ret_stamp, ret_list)

    """ test feet pos msg """
    feetpos_list = [[420, 69.2, 0], [69, 69, 0]]
    msg_bytes = FeetPositionMsg.pack(ts, feetpos_list)

    # unpack message
    ret_id, ret_stamp, ret_list= SkaiMsg.unpack(msg_bytes)
    print(ret_id, ret_stamp, ret_list)
