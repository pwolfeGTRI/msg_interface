#!/usr/bin/python3

# if it breaks contact: Philip Wolfe <pwolfe854@gmail.com>

from skaimsginterface.replay.FileRecorder import FileRecorder
import multiprocessing

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import TcpSender
from skaimsginterface.udp import UdpSender

class ReplayModule:
    def __init__(self, filepath, udp_or_tcp, analyze_only=False, camgroupchange=None) -> None:
        self.analyze_only = analyze_only

        # parses file to get list of tuples: (timestamp, port, bytes2replay)
        retlist = FileRecorder.parseRecordedFileForReplay(filepath)

        print(f'ReplayModule parsed {filepath} for total of {len(retlist)} messages')

        self.udp_or_tcp = udp_or_tcp
        
        # separate into dictionary format: d[port] = (timestamp, bytes2replay)
        d = self.separateIntoPorts(retlist)
        print(f'camera group number: {self.getCameraGroupNum(d)}')
        for port in d.keys():
            print(f"port {port} has {len(d[port])} messages")
           
        # order by timestamp & calc wait duration between messages
        # new format: d[port] = (duration, bytes2replay)
        for port in d.keys():
            d[port] = self.orderPortListByTimestamp(d[port])
            
        # calc earliest time among the ports and duration based on that
        d = self.calcWaitTimeBeforeSend(d)

        # remap camera group ports if desired
        if camgroupchange is not None:
            d = self.remapToNewCameraGroup(d, camgroupchange)

        # store reference ready for replay
        self.replay_dictionary = d

    def replay(self):
        if self.analyze_only:
            print('analyze only enabled. not replaying...')
            return

        print('starting replay processes...')
        portlist = self.replay_dictionary.keys()
        max_processes = len(portlist)
        with multiprocessing.Pool(processes=max_processes) as p:
            argslist = [(self.udp_or_tcp, p, self.replay_dictionary[p]) for p in portlist]
            p.map(self.singlePortReplay, argslist)

    @staticmethod
    def singlePortReplay(argsTuple):
        udp_or_tcp, port, port_replay_list = argsTuple
        # port_replay_list is list of tuples (waitTime, bytes2send)
        # where waitTime is time to wait before sending bytes2send on port
        # TcpSend

        if udp_or_tcp == 'udp':
            sender = UdpSender('127.0.0.1', port, verbose=True)
        else:    
            sender = TcpSender('127.0.0.1', port, verbose=True)

        print(f'replaying on port {port} ...')
        for waitTime, bytes2send in port_replay_list:
            time.sleep(waitTime)
            sender.send(bytes2send)
        print(f'done sending messages on port {port}!')


    def attemptToKillAllReplayProcesses(self):
        pass

    @staticmethod
    def separateIntoPorts(retlist):
        # retlist is list of tuples: (timestamp, port, bytes2replay)
        d = {}
        for timestamp, port, bytes2replay in retlist:
            if port in d:
                d[port].append( (timestamp, bytes2replay) )
            else:
                d[port] = [ (timestamp, bytes2replay) ]
        return d

    @staticmethod
    def orderPortListByTimestamp(port_retlist):
        # port_retlist is list of format (timestamp, bytes2replay) for a port
        x = port_retlist
        x = sorted(x, key=lambda x: x[0])
        return x

    @staticmethod
    def calcWaitTimeBeforeSend(port_dict):
        pass
        # find the earliest timestamp among ports
        t0 = min([x[0][0] for x in port_dict.values()])
        # make new port dictionary with lists of (waitTime, bytes2send)
        d = {}
        for port in port_dict.keys():
            # create empty list
            d[port] = []
            # init prevTime to be earliest timestamp among ports
            prevTime = t0
            # populate port list with (waitTime, bytes2send)
            for timestamp, bytes2send in port_dict[port]:
                waitTime = timestamp - prevTime
                d[port].append( (waitTime, bytes2send) )
                prevTime = timestamp
        # return new dictionary
        return d

    @classmethod
    def remapToNewCameraGroup(cls, port_dict, newcamgroup):
        original_camgroup = cls.getCameraGroupNum(port_dict)
        d = {}
        for port in port_dict.keys():
            portstr = str(port)
            newport = int(portstr[:2] + str(newcamgroup))
            d[newport] = port_dict[port]
        return d

    @staticmethod
    def getCameraGroupNum(port_dict):
        port = list(port_dict.keys())[0]
        portstr = str(port)
        if len(portstr) != 4:
            raise ValueError(f'{port} is invalid port type. must be 4 digits long')
        camgroupnum = int(portstr[-2:])
        return camgroupnum


if __name__=='__main__':
    
    rpm = ReplayModule('localtest.skaibin', 'tcp')
    # print(rpm.replay_dictionary)
    
    # # test replay first port in dict keys
    # port = list(rpm.replay_dictionary.keys())[0]
    # port_replay_list = rpm.replay_dictionary[port]
    # ReplayModule.singlePortReplay( ('tcp', port, port_replay_list) )

    rpm.replay()

    # code.interact(local=locals())  
    

    