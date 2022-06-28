#!/usr/bin/python3

from argparse import ArgumentParser
from skaimsginterface.skaimessages import *
from skaimsginterface.replay import ReplayModule

if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument('skaibin_file', type=str, help='skaibin file to replay from')
    parser.add_argument('udp_or_tcp', type=str, help='', choices=('tcp', 'udp'))
    parser.add_argument('--analyzeonly', help='only analyzes. doesn\'t replay', nargs='?', const=True, default=False)
    args = parser.parse_args()
    
    if args.analyzeonly:
        action_str = 'analyzing'
    else:
        action_str = 'replaying'
    print(f'\n{action_str} {args.udp_or_tcp} messages from skaibin file: {args.skaibin_file}\n')
    rpm = ReplayModule(args.skaibin_file, args.udp_or_tcp, analyze_only=args.analyzeonly)
    rpm.replay()

