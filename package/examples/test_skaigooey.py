#!/usr/bin/python3
import time
from pathlib import Path
from argparse import ArgumentParser

from skaimsginterface.skaimessages import *
from skaimsginterface.tcp import TcpSender
from skaimsginterface.udp import UdpSender

def create_example_skaigooeymsg():
    msg = SkaiGooeyMsg.new_msg()
    # put nothing in it for now. make Pawel do more work :P 
    return msg


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('udp_or_tcp', type=str,
                        help='protocol to listen on', choices=('tcp', 'udp'))
    parser.add_argument('--exampleout', help='dump an example message text file under a folder example_msg_prints',
                        nargs='?', type=bool, const=True, default=False)
    # parser.add_argument(
    #     '--camgroup', help='camera group number (default 0)', nargs='?', type=int, default=0)
    args = parser.parse_args()

    # create example  message
    msg = create_example_skaigooeymsg()
    # print(msg)

    # write example message to file for viewing
    if args.exampleout:
        filename = 'example_msg_prints/skai_gooey.txt'
        print(f'wrote example message to {filename}')
        p = Path(filename)
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_text(f'{msg}')

    msg_bytes = SkaiGooeyMsg.pack(msg, verbose=True)
    if args.udp_or_tcp == 'udp':
        sender = UdpSender(
            '127.0.0.1', SkaiGooeyMsg.ports[4], verbose=True)
    else:
        sender = TcpSender(
            '127.0.0.1', SkaiGooeyMsg.ports[4], verbose=True)
    sender.send(msg_bytes)
