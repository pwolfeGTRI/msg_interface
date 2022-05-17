#!/usr/bin/python3

import struct
import time
from datetime import datetime

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

class SkaimotMsg(SkaiMsg):
    """SkaiMOT message packing/unpacking/port definitions"""
    port = 6940

    @staticmethod
    def pack(timestamp, trackid_list=None, bbox_list=None, face_embed_list=None, bbox_embed_list=None):
        """ 
        packed data format
            msgid (uint16)
            timestamp (double)
            
            number of tracks (uint16)
            tracklist [id, id, id]
            
            number of bboxes (uint16)
            bbox_list [ [ul_x, ul_y, br_x, br_y], ... ] floats
            
            number of face embed (uint16)
            face_embed_list[ [512 floats], ...]
            
            number of bbox embed (uint16)
            bbox_embed_list[ [2048 floats], ...]

        """
        msg_bytes = struct.pack('! H d', MsgType.SKAIMOT.value, timestamp)

        if trackid_list is None:
            msg_bytes += struct.pack('! H', 0) # zero if None
        else:
            count = len(trackid_list)
            msg_bytes += struct.pack('! H', count)
            if count > 0:
                msg_bytes += struct.pack(f'! {count}I', *trackid_list)
            
        # bbox [ul_x, ul_y, br_x, br_y]
        if bbox_list is None:
            msg_bytes += struct.pack('! H', 0) # zero if None
        else:
            count = len(bbox_list)
            msg_bytes += struct.pack('! H', count)
            if count > 0:
                for entry in bbox_list:
                    msg_bytes += struct.pack('! 4f', *entry)
        
        # face embedding [512 floats]
        if face_embed_list is None:
            msg_bytes += struct.pack('! H, 0') # zero if None
        else:
            count = len(face_embed_list)
            msg_bytes += struct.pack('! H', count)
            if count > 0:
                for entry in face_embed_list:
                    msg_bytes += struct.pack('! 512f', *entry)

        # bbox embedding [2048 floats]
        if bbox_embed_list is None:
            msg_bytes += struct.pack('! H', 0) # zero if None
        else:
            count = len(bbox_embed_list)
            msg_bytes += struct.pack('! H', count)
            if count > 0:
                for entry in face_embed_list:
                    msg_bytes += struct.pack('! 2048f', *bbox_embed_list)

        return msg_bytes        

    @classmethod
    def unpack(cls, msg_bytes):
        print(f'unpacking {cls.__name__}')

        # get message id and timestamp
        msgid, timestamp = struct.unpack('! H d', msg_bytes[:10])
        idx = 10
        
        # init as None
        trackid_list = None
        bbox_list = None
        face_embed_list = None
        bbox_embed_list = None

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
            bbox_list = []
            element_size = 4
            for i in range(count):
                bbox_list.append( struct.unpack(f'! {element_size}f', msg_bytes[idx:idx+element_size*4]) )
                idx += element_size*4

        # face embed list
        count = struct.unpack('! H', msg_bytes[idx:idx+2])[0]
        idx += 2
        if count > 0:
            face_embed_list = []
            element_size = 512
            for i in range(count):
                face_embed_list.append( struct.unpack(f'! {element_size}f', msg_bytes[idx:idx+element_size*4]) )
                idx += element_size*4
        
        # bbox embed list
        count = struct.unpack('! H', msg_bytes[idx:idx+2])[0]
        idx += 2
        if count > 0:
            bbox_embed_list = []
            element_size = 2048
            for i in range(count):
                bbox_embed_list.append( struct.unpack(f'! {element_size}f', msg_bytes[idx:idx+element_size*4]) )
                idx += element_size*4

        return msgid, timestamp, trackid_list, bbox_list, face_embed_list, bbox_embed_list

class PoseMsg(SkaiMsg):
    """Pose message packing/unpacking/port definitions"""
    port = 6941
    
    @classmethod
    def pack(cls, msg_bytes):
        print(f'packing {cls.__name__}')
        return f'packed {cls.__name__} here'

    @classmethod
    def unpack(cls, msg_bytes):
        print(f'unpacking {cls.__name__}')
        return f'unpacked {cls.__name__} here'

class FeetPositionMsg:
    """Feet position message packing/unpacking/port definitions"""
    port = 6942
    
    @classmethod
    def pack(cls, msg_bytes):
        print(f'packing {cls.__name__}')
        return f'packed {cls.__name__} here'

    @classmethod
    def unpack(cls, msg_bytes):
        print(f'unpacking {cls.__name__}')
        return f'unpacked {cls.__name__} here'

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


class StandardMessages:
    @staticmethod
    def unpack_bbox_msg(msg_bytes):
        # bbox_list format (1 frame):
        # [ [id, tl_x, tl_y, bl_x, bl_y], [id, tl_x, tl_y, bl_x, bl_y], ...]
        pass
        # unpack timestamp and number of boxes from first 12 bytes
        timestamp, num_boxes = struct.unpack('! d I', msg_bytes[:12])
        idx = 12
        boxes = []
        for i in range(num_boxes):
            box = struct.unpack('!5f', msg_bytes[idx:idx+5*4])
            boxes.append(box)
            idx += 5*4
        return timestamp, boxes


import numpy as np

if __name__=='__main__':
    # pack message
    ts = time.time() # use double not float
    trackid_list = [42, 69]
    bbox_list = [[0.2, 0.21, 0.4, 0.42], [0.2, 0.21, 0.4, 0.42]]
    face_embed_list = [ np.arange(512).tolist(), np.arange(512).tolist()]
    msg_bytes = SkaimotMsg.pack(ts, trackid_list, bbox_list, face_embed_list)
    
    # unpack message
    print(SkaiMsg.unpack(msg_bytes))
        
