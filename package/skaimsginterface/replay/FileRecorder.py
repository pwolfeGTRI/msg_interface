#!/usr/bin/python3

from skaimsginterface.skaimessages import *
import struct

class FileRecorder:
    def __init__(self, filepath, append=False) -> None:
        self.filepath = filepath
        self.modifier = 'ab' if append else 'wb'
        self.fd = None

    def open(self):
        # open with either append or write binary
        print(f'opening file {self.filepath} in mode {self.modifier}')
        self.fd = open(self.filepath, self.modifier)

    def close(self):
        if self.fd is not None:
            self.fd.close()
            self.fd = None
        else:
            print('Cannot close file if never opened')

    def record(self, msg_bytes, epoch_timestamp, port):
        """ 
            params:
                msgbytes: bytes result of msgtype.pack(protobuf)
                epoch_timestamp (double): epoch time
                port (uint16): the port received on

            ret:
                success (bool): whether recording was successful or not
        """
        if self.fd is None:
            print('cannot write if recorder is not opened yet. call the open() function first')
            # return success = False
            return False

        # pack msg type + protobuf serialized according to SkaiMsg type
        # append timestamp (double) port(uint16) & length (integer)
        msg_bytes = struct.pack('!dHI', epoch_timestamp, port, len(msg_bytes)) + msg_bytes
        # write to file
        print('writing to file...')
        self.fd.write(msg_bytes)

        # return success = True
        return True
        

    @classmethod 
    def parseRecordedFileForReadability(cls, filepath):
        """
            returns:
                list of tuples of form (timestamp, port, SkaiMsg.MsgType, Protobuf)
        """
        retlist = []
        replaylist = cls.parseRecordedFileForReplay(filepath)
        for timestamp, port, bytes2replay in replaylist:
            msgtype, protobuf = SkaiMsg.unpack(bytes2replay)
            retlist.append( (timestamp, port, msgtype, protobuf) )
        return retlist

    @classmethod
    def parseRecordedFileForReplay(cls, filepath):
        """
            returns:
                list of tuples of form (timestamp, port, bytes2replay)
        """
        msgbytes = cls._readRecordedBytes(filepath)
        retlist = []
        idx = 0
        while idx < len(msgbytes):
            # unpack timestamp & length
            headerlen = 8+2+4
            timestamp, port, length = struct.unpack('!dHI', msgbytes[idx:idx+headerlen])
            # increment to start of SkaiMsg
            idx += headerlen
            # unapck message type and message
            bytes2replay = msgbytes[idx:idx+length]
            retlist.append( (timestamp, port, bytes2replay) )
            idx += length

        return retlist

    @staticmethod
    def _readRecordedBytes(filepath):
        with open(filepath, 'rb') as f:
            ret = f.read()
        return ret


if __name__=='__main__':
    from examples.test_skaimot import create_example_skaimotmsg
    from examples.test_feetpos import create_example_feetposmsg
    from skaimsginterface.skaimessages import *

    import code

    # create test message, timestamp of first packet, and port
    msg1 = create_example_skaimotmsg(num_cams=1, num_people=1)
    msg2 = create_example_feetposmsg(num_cams=1, num_people=1)
    msg1bytes = SkaimotMsg.pack(msg1)
    msg2bytes = FeetPosMsg.pack(msg2)

    timestamp1 = time.time() # log time of full message arrival in listener
    time.sleep(0.42)
    timestamp2 = time.time() 

    camgroup_idx = 0
    port1 = SkaimotMsg.ports[camgroup_idx]
    port2 = FeetPosMsg.ports[camgroup_idx]

    print(f'created msg1: {msg1}')
    print(f'created msg2: {msg2}')

    recorder = FileRecorder('testrecorder.skaibin')
    recorder.open()
    recorder.record(msg1bytes, timestamp1, port1)
    recorder.record(msg2bytes, timestamp2, port2)
    recorder.close()

    retlist1 = FileRecorder.parseRecordedFileForReplay('testrecorder.bin')
    retlist2 = FileRecorder.parseRecordedFileForReadability('testrecorder.bin')

    code.interact(local=locals())
