#!/usr/bin/env python3

from argparse import ArgumentParser

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import MultiportTcpListenerMP
# from skaimsginterface.udp import MultiportUdpListenerMP TODO implement this later

def example_multiport_callback_func(data, server_address):
    # store it, unpack, etc do as you wish
    msg_type, msg = SkaiMsg.unpack(data)
    print(f'got some data length {len(data)} from {server_address} msg type {msg_type}\n')
    # unpack_and_print_cam_id_and_timestamp_per_frame(data)
    # print(msg)
    # print(msg.camera_frames[0].people_in_frame)
    # print(msg.camera_frames[0].people_in_frame[0].orientation)

def unpack_and_print_cam_id_and_timestamp_per_frame(msg_bytes):
    # unpack message
    msg_type, msg = SkaiMsg.unpack(msg_bytes)
    print(f'got msg type {msg_type}, data: {msg}')
    for frame_data in msg.camera_frames:
        # print camera id and timestamp
        print(f'cam id: {frame_data.camera_id}, timestamp: {frame_data.timestamp}')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('udp_or_tcp', type=str, help='protocol to listen on', choices=('tcp', 'udp'))
    parser.add_argument('--camgroup', help='camera group number (default 0)', nargs='?', type=int, default=0)
    parser.add_argument('--recordfile', help='skaibin file to record to', nargs='?', type=str, default=None)
    parser.add_argument('--ipv6', help='use ipv6 instead of ipv4 default', nargs='?', type=bool, const=True, default=False)
    args = parser.parse_args()

    # check for ipv6 loopback
    if args.ipv6:
        print(f'please make sure you\'ve enabled ipv6 and ipv6 loopback')
        print(f'\tsudo sysctl -w net.ipv6.conf.eth0.disable_ipv6=0')
        print(f'\tsudo sysctl -w net.ipv6.conf.lo.disable_ipv6=0')
        print(f'\nalso ensure that you enabled ipv6 docker support on your system')
        print(f'(modify /etc/docker/daemon.json and restart and also setup appropriate ipvlan per container)')
        input('press enter to acknowledge...')
    # exit(1)
    # ports to listen to
    camgroup_idx = args.camgroup
    dealership_test_idx = 4
    ports = [
        SkaimotMsg.ports[camgroup_idx],
        PoseMsg.ports[camgroup_idx],
        FeetPosMsg.ports[camgroup_idx],
        LocalTrackMsg.ports[camgroup_idx],
        GlobalTrackMsg.ports[camgroup_idx],
        ActionMsg.ports[camgroup_idx],
        TracksInDealershipMsg.ports[dealership_test_idx],
        InteractionInDealershipMsg.ports[dealership_test_idx],
        VehicleMsg.ports[camgroup_idx],
        VehicleSpotMonitorMsg.ports[camgroup_idx],
        SkaiEventMsg.ports[camgroup_idx],
        SkaiGooeyMsg.ports[4] # only 1 per dealership (range 0 to 9 available. using num 4 for testing)
        ]

    # make a print_q for multiprocessing
    import multiprocessing as mp
    print_q = mp.SimpleQueue()

    # listen
    if args.udp_or_tcp == 'udp':
        print('multiprocessing udp support not implemented yet')
        # listener = MultiportUdpListener(
        #     portlist=ports,
        #     multiport_callback_func=example_multiport_callback_func,
        #     recordfile=args.recordfile,
        #     verbose=True)
    else:
        listener = MultiportTcpListenerMP(
            portlist=ports,
            multiport_callback_func=example_multiport_callback_func,
            print_q=print_q,
            recordfile=args.recordfile,
            ipv6=args.ipv6,
            verbose=True)

    # stay active until ctrl+c input
    try:
        while True:
            if not print_q.empty():
                print(print_q.get())
            time.sleep(0.001)
    except KeyboardInterrupt:
        print('exiting now...')
        
        # wait a second
        time.sleep(1)

        # print remaining print_q?
        while not print_q.empty():
            print(print_q.get())

        # actually stop listeners
        listener.stop()

