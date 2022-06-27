#!/usr/bin/python3

from argparse import ArgumentParser
from skaimsginterface.skaimessages import *
from skaimsginterface.replay import ReplayModule

if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument('skaibin_file', type=str, help='skaibin file to replay from')
    parser.add_argument('udp_or_tcp', type=str, help='', choices=('tcp', 'udp'))
    args = parser.parse_args()
    
    print(f'\nreplaying {args.udp_or_tcp} messages from skaibin file: {args.skaibin_file}\n')

    rpm = ReplayModule(args.skaibin_file, args.udp_or_tcp)
    rpm.replay()

