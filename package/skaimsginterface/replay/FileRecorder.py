#!/usr/bin/python3

# if it breaks contact: Philip Wolfe <pwolfe854@gmail.com>

from skaimsginterface.skaimessages import *
import struct
from pathlib import Path
from queue import Queue, Empty
from threading import Thread
import multiprocessing as mp

class FileRecorder:
    def __init__(self, filepath, append=False) -> None:       
        # check filepath ends in skaibin
        if not isinstance(filepath, str):
            raise TypeError('FileRecorder file must by type str')
        if filepath.split('.')[-1] != 'skaibin':
            raise ValueError('FileRecorder file must end in ".skaibin"')
        
        self.filepath = filepath
        self.modifier = 'ab' if append else 'wb'
        self.fd = None

    def open(self):
        # create directory if needed
        self.create_directory_if_needed(self.filepath)
        # open with either append or write binary
        print(f'opening file {self.filepath} in mode {self.modifier}')
        self.fd = SafeWriter(self.filepath, self.modifier)
        # self.fd = open(self.filepath, self.modifier)

    @staticmethod
    def mp_record_process(stop_event, print_q, msg_in_q, filepath, append=False, verbose=False):

        # check filepath is str and ends in skaibin
        if not isinstance(filepath, str):
            raise TypeError('FileRecorder file must by type str')
        if filepath.split('.')[-1] != 'skaibin':
            raise ValueError('FileRecorder file must end in ".skaibin"')
        
        # create directory if needed and decide to open and write to file fresh or append
        FileRecorder.create_directory_if_needed(filepath)
        modifier = 'ab' if append else 'wb'

        try:
            # open file
            print_q.put(f'recording to file {filepath}, append={append}')
            f = open(filepath, modifier)
            
            # query queue and write to file when not empty
            while not stop_event.is_set():
                if not msg_in_q.empty():
                    # get info from queue
                    msg_bytes, epoch_timestamp, port = msg_in_q.get()
                            
                    # pack msg type + protobuf serialized according to SkaiMsg type
                    # append timestamp (double) port(uint16) & length (integer)
                    msg_bytes = struct.pack('!dHI', epoch_timestamp, port, len(msg_bytes)) + msg_bytes
                    if verbose:
                        print_q.put(f'writing to file...')

                    # write to file
                    f.write(msg_bytes)

        except Exception as e:
            print_q.put(f'mp_record_process got exception {e}')
        finally:
            print_q.put(f'mp_record_process closing file {filepath}')
            f.close()
            


    @staticmethod
    def create_directory_if_needed(filepath):
        p = Path(filepath)
        p.parent.mkdir(exist_ok=True, parents=True)

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
        return Path(filepath).read_bytes()

class SafeWriter:
    def __init__(self, *args):
        self.filewriter = open(*args)
        self.queue = Queue()
        self.finished = False
        Thread(name = "SafeWriter", target=self.internal_writer).start()  
    
    def write(self, data):
        self.queue.put(data)
    
    def internal_writer(self):
        while not self.finished:
            try:
                data = self.queue.get(True, 1)
            except Empty:
                continue    
            self.filewriter.write(data)
            self.queue.task_done()
    
    def close(self):
        self.queue.join()
        self.finished = True
        self.filewriter.close()

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
