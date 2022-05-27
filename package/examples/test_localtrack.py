#!/usr/bin/python3
from skaimsginterface.skaimessages import *
from test_skaimot import create_example_skaimotmsg
from test_pose import create_example_posemsg
from test_feetpos import create_example_feetposmsg

# import code 
# variables = globals().copy()
# variables.update(locals())
# shell = code.InteractiveConsole(variables)
# shell.interact()



if __name__=='__main__':

    # create example base messages
    skaimotmsg = create_example_skaimotmsg()
    posemsg = create_example_posemsg()
    feetposmsg = create_example_feetposmsg()

    # use to populate local track message
    msg = LocalTrackMsg.new_msg()
    msg.id = skaimotmsg.id
    msg.camera_id = 56789 # copy over from skaimot msg
    # copy over from skaimot msg if first time (default value is 0)
    if msg.time_discovered == 0:
        msg.time_discovered = 12345 
    
    # populate metadata lists
    bbox = msg.bbox_list.add()
    bbox.timestamp = 12345 # copy from skaimot
    # LocalTrackMsg.copy_bbox(bbox, skaimotBbox)
    
