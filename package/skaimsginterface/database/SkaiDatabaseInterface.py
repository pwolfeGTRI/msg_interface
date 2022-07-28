#!/usr/local/bin/python3

import json
from urllib.parse import urljoin
import requests
import ast

import code

import numpy as np

class SkaiDatabaseInterface:

    CAMERA_REQUIRED_FIELDS = {'camera_mac_address'}

    CAMERA_FIELDS = { # should be a copy of Camera model in models.py
        'camera_id',
        'mac_address',
        'ip_address',
        'stream_uri',
        'processing_group',
        'cam_matrix',
        'dist_coeff',
        'orig_res',
        # 'calib_resolution',
        # 'position',
        # 'quaternion',
        # 'homography',
        # 'floor_eq',
        # 'cam_to_floor'
        'cam_pose',
        'plane_eq'
    }

    JSON_FIELDS = {
        'cam_matrix',
        'dist_coeff',
        'orig_res',
        'cam_pose',
        'plane_eq'
    }

    def __init__(self,
                 verbose=False,
                 database_url='http://127.0.0.1:8845'):
        self.verbose = verbose
        self.url = database_url

    def _database_write(self, url_ext, msg, update=False):
        """private database write function that sends post req

        Args:
            url_ext (str): specific subpage to post to. use double quote strings only
            msg (dict): python dictionary 
        """
        assert type(msg) == dict
        assert type(url_ext) == str

        # safely join url (removes redundant slashes)
        full_url = urljoin(
            self.url, url_ext)
        if not update:
            full_url += '/'  # adding slash is required for posting
        # safely convert single string to double string in dicitonary
        # print(f'msg before: {msg}')
        msg = json.loads(json.dumps(msg))
        # print if verbose
        if self.verbose:
            print('\nPOSTing:')
            print(f'\tdestination url: {full_url}')
            print(f'\tmsg: {msg}\n')
        ret = requests.post(full_url, json=msg)
        if self.verbose:
            print('got response:')
            print(f'\t{ret.json()}')
        return ret

    def _database_update(self, url_ext, msg, db_id):
        # safely join url (removes redundant slashes)
        full_url = urljoin(
            self.url, url_ext) + '/'  # adding slash is required for posting
        # safely convert single string to double string in dicitonary
        # print(f'msg before: {msg}')
        full_url += f'{db_id}/'
        msg = json.loads(json.dumps(msg))
        # print if verbose
        if self.verbose:
            print('\nPUTTINGing:')
            print(f'\tdestination url: {full_url}')
            print(f'\tmsg: {msg}\n')
        ret = requests.put(full_url, json=msg)
        if self.verbose:
            print('got response:')
            print(f'\t{ret.json()}')
        return ret

    def _database_read(self, url_ext, id=None):
        """private database read function that sends get req

        Args:
            url_ext (str): specific subpage to read from
            id (int, optional): specific message id. Defaults to None.


        Returns:
            object: requests return object with data 
        """
        full_url = urljoin(self.url, url_ext)
        if id is not None:
            full_url += f'/{id}'
        if self.verbose:
            print('GETting:')
            print(f'\tdestination url: {full_url}')
        ret = requests.get(full_url)
        return ret

    # def _unpack_json_fields(self, obj):
    #     if type(obj) == list:
    #         for _obj in obj:
    #             for key in _obj.keys():
    #                 if key in self.JSON_FIELDS:
    #                     if _obj[key] != None:
    #                         _obj[key] = _obj[key][key]
    #     else:
    #         for key in obj.keys():
    #             if key in self.JSON_FIELDS:
    #                 if obj[key] != None:
    #                     obj[key] = obj[key][key]
    
    # def _pack_json_fields(self, obj):
    #     if type(obj) == list:
    #         for _obj in obj: 
    #             for key in _obj.keys():
    #                 if key in self.JSON_FIELDS:
    #                     if _obj[key] != None:
    #                         _obj[key] = {key: _obj[key]}
    #     else:
    #         for key in obj.keys():
    #             if key in self.JSON_FIELDS:
    #                 if obj[key] != None:
    #                     obj[key] = {key: obj[key]}

    def _check_for_null_fields(self, obj):
        if isinstance(obj, list):
            [self._check_for_null_fields(_obj) for _obj in obj]
        else:
            for key, val in obj.items():
                if val is None:
                    print(f'Warning: found {key} is {val} inside json object')

    def write_bboxes(self, bbox_list, timestamp=None):
        """writes bounding box (bbox) data and timestamp

        Args:
            bbox_list (list): list of bounding boxes in format [id, x, y, w, h] in a frame where
                id (int): track box id
                x (int): center bbox column coordinate in pixels (upper left is 0,0)
                y (int): center bbox row coordinate in pixels (upper left is 0,0)
                w (int): width of bbox in pixels
                h (int): height of bbox in pixels
            camera_ip (str, optional): camera ip address string. example "192.168.69.69"
            timestamp (datetime, optional): Todo: implement this override. for now appends timestamp of arrival at database

            TODO type check
        Return:
            True/False for if you wrote correctly
        """
        if not isinstance(bbox_list, list):
            print('bbox_list type must be list')
            return False
        if len(bbox_list) == 0:
            print('bbox_list must have at least one bbox')
            return False
        if not isinstance(bbox_list[0], list):
            print('bbox_list entries must be lists. example: [trackid, x, y, w, h]')
            print(type(bbox_list[0]))
            return False
        if len(bbox_list[0]) != 5 or (not isinstance(bbox_list[0][0], int)):
            print('bbox_list entries must be lists of length 5 with type int: [trackid, x, y, w, h]')
            return False
        

        msg = {"bounding_box": bbox_list}
        self._database_write('boxes', msg)

    def read_bboxes(self, id=None):
        """reads bounding boxes (bbox) or a specific bbox id if param provided

        Args:
            id (int, optional): specific message id. Defaults to None.

        Returns:
            dict  : json dictionary of what you requested
        """
        ret = self._database_read('boxes', id)
        # maybe do different parsing all or specific id?? think about later
        if ret.status_code != 204:
            parsed = ret.json()
        else:
            parsed = ret.status_code
        return parsed

    def write_poses(self, poses_in_frame, camera_ip=None):
        """writes pose keypoints per person in a frame to database

        Args:
            poses_in_frame (list): list of keypoints
            camera_ip (str): camera ip address string. example "192.168.69.69"
        
        Notes:
            keypoints  (list): list of 18 pairs. example: [[1,1], .... [18,18]]
            
        """
        msg = {"poses": poses_in_frame}
        self._database_write('poses', msg)

    def read_poses(self, id=None):
        """reads all frames of poses or a specific frame id. note frame id for demo is not in sync with rest of database

        Args:
            id (int, optional): poses frame id to read from database. Defaults to None.

        Returns:
            dict: json dictionary of what you requested
        """
        ret = self._database_read('poses', id)
        if ret.status_code != 204:
            parsed = ret.json()
        else:
            parsed = ret.status_code
        return parsed

    def write_feet_positions(self, xyz_feet_pos_list, camera_ip=None):
        """writes a list of feet positions datatypes in frame to database

        Args:
            xyz_feet_pos_list (list): list of feet_positions
        Notes:
            feet_positions: [track_id, x, y, z] 3d space coordinate (type float, units meters)
        """
        msg = {"pos": xyz_feet_pos_list}
        self._database_write('feet_positions', msg)

    def read_feet_positions(self, id=None):
        """read all current foot positions from database across all frames and all cameras for all of time
        
        Args:
            id (int, optional): specific message id. Defaults to None.

        Returns:
            foot_positions (list): list of foot_position datatypes to read from database
                foot_position datatype: [x, y, z] where x,y,z are floats and in meters
        """
        ret = self._database_read('feet_positions', id)
        # do  list datatype parsing here if you want
        # for testing i'll just leave it same
        parsed = ret.json()  #['results']
        return parsed

    def write_alerts(self, event:str, alert_time=None):
        """write an alert event at a time(will default to time of database entry if not specified)

        Args:
            event (str): event string 
            alert_time (DateTime, optional): date time to override if don't want time of database entry. Defaults to None.
        """
        msg = {
            "event": event,
        }
        if alert_time is not None:
            msg['alert_time'] = alert_time

        self._database_write('alerts', msg)

    def read_alerts(self, id=None):
        ret = self._database_read('alerts', id)
        parsed = ret.json()
        return parsed

    def set_camera_calibration_details(self, mac_address, **msg): 
        # msg = {
        #     "camera_mac_addr": 42,
        #     "serial_number": 69,
        #     "ip_address": "2.1.1.1",
        #     "camera_matrix": {},
        #     "dist_coef": {},
        #     "calib_resolution": "[1,2]",
        #     "position": {},
        #     "quaternion": {},
        #     "homography": {},
        #     "floor_eq": {},
        #     "cam_to_floor": {}
        # }
        keyset = set(msg.keys())
        if not keyset.issubset(self.CAMERA_FIELDS):
            unique = ', '.join([str(k) for k in keyset-self.CAMERA_FIELDS])
            raise ValueError(f'Fields do not belong in Camera: {unique}')
        # self._pack_json_fields(msg)

        url = f"cameras/set_calibration_details/{mac_address}"
        ret = self._database_write(url, msg, update=True)
        parsed = ret.json()
        # self._unpack_json_fields(parsed)
        return parsed

    def set_camera_connection_details(self, mac_address, **msg):
        keyset = set(msg.keys())
        if not keyset.issubset(self.CAMERA_FIELDS):
            unique = ', '.join([str(k) for k in keyset-self.CAMERA_FIELDS])
            raise ValueError(f'Fields do not belong in Camera: {unique}')

        url = f"cameras/set_connection_details/{mac_address}"
        ret = self._database_write(url, msg, update=True)
        parsed = ret.json()
        # self._unpack_json_fields(parsed)
        return parsed 

    def set_camera_processing_group(self, mac_address, **msg):
        keyset = set(msg.keys())
        if not keyset.issubset(self.CAMERA_FIELDS):
            unique = ', '.join([str(k) for k in keyset-self.CAMERA_FIELDS])
            raise ValueError(f'Fields do not belong in Camera: {unique}')

        url = f"cameras/set_processing_group/{mac_address}"
        ret = self._database_write(url, msg, update=True)
        parsed = ret.json()
        # self._unpack_json_fields(parsed)
        return parsed 

    def write_camera(self, **msg):
        keyset = set(msg.keys())
        if self.CAMERA_REQUIRED_FIELDS.issubset(keyset):
            required = ', '.join([str(k) for k in self.CAMERA_REQUIRED_FIELDS-keyset])
            raise ValueError(f'Required fields not found: {required}')
        elif not keyset.issubset(self.CAMERA_FIELDS):
            unique = ', '.join([str(k) for k in keyset-self.CAMERA_FIELDS])
            raise ValueError(f'Fields do not belong in Camera: {unique}')

        ret = self._database_write('cameras', msg)
        parsed = ret.json()
        return parsed

    # def write_cameras(self, mac_addr, ip_address, camera_matrix, dist_coef, 
    #     calib_resolution, position, quaternion, homography,
    #     floor_eq, cam_to_floor, serialnum=None):
    #     """writes to camera database

    #     Args:
    #         ip_address (str): ip address string
    #         camera_matrix (list): float[3][3]
    #         dist_coef (list): float[14]
    #         calib_resolution (list): int[2]
    #         position (list): float[3]
    #         quaternion (list): float[4]
    #         homography (list): float[4,3]
    #         floor_eq (list): float[4]
    #         cam_to_floor (list): [4,4]
    #         serialnum (int, optional): camera serial number. Defaults to None.
    #     """
    #     msg = {
    #         "camera_mac_addr": 420,
    #         "serial_number": 690,
    #         "ip_address": "1.1.42.69",
    #         "camera_matrix": {},
    #         "dist_coef": {},
    #         "calib_resolution": "[21,23]",
    #         "position": {},
    #         "quaternion": {},
    #         "homography": {},
    #         "floor_eq": {},
    #         "cam_to_floor": {}
    #     }
    #     # msg = {
    #     #     "camera_mac_addr": 1,
    #     #     "serial_number": 42069,
    #     #     "ip_address": "1.1.1.1",
    #     #     "camera_matrix": test,
    #     #     "dist_coef": test,
    #     #     "calib_resolution": str(calib_resolution), # change list to str before write
    #     #     "position": test,
    #     #     "quaternion": test,
    #     #     "homography": test,
    #     #     "floor_eq": test,
    #     #     "cam_to_floor": test,
    #     # }
    #     # if serialnum != None:
    #     #     msg["serial_number"] = serialnum

    #     self._database_write('cameras', msg)

    def get_camera_by_mac_address(self, mac_address):
        ret = self._database_read('cameras/get_by_mac_address', mac_address)
        parsed = ret.json()
        # self._unpack_json_fields(parsed)
        return parsed

    def get_cameras_by_processing_group(self, processing_group):
        ret = self._database_read('cameras/get_by_processing_group', processing_group)
        parsed = ret.json()
        # self._unpack_json_fields(parsed)
        return parsed
        
    # def read_cameras(self, id=None):
    #     ret = self._database_read('cameras', id)
    #     parsed = ret.json()  
        
    #     # change calib_resolution str to list before return
        
    #     # handle differently if all results vs single entry
    #     if 'results' in parsed:
    #         for results in parsed['results']:
    #             results['calib_resolution'] = ast.literal_eval(results['calib_resolution'])
    #     else:
    #         results = parsed
    #         results['calib_resolution'] = ast.literal_eval(results['calib_resolution'])
        
    #     return parsed

    def remove_camera_by_mac_address(self, mac_address):
        ret = self._database_write(f"cameras/remove_by_mac_address/{mac_address}", dict(), update=True)
        parsed = ret.json()
        self._check_for_null_fields(parsed)
        # self._unpack_json_fields(parsed)
        return parsed

    def remove_cameras_by_processing_group(self, processing_group):
        ret = self._database_write(f"cameras/remove_by_processing_group/{processing_group}", dict(), update=True)
        parsed = ret.json()
        self._check_for_null_fields(parsed)
        # self._unpack_json_fields(parsed)
        return parsed

    def write_local_tracks(self,
        classification, camera_id, active, discovered=None,
        local_track_boxes=None, local_track_poses=None, interactions=None,
        feet_pos=None, face_embedding=None, bbox_embedding=None):
        
        msg = {
            "classification": classification,
            "camera_id": camera_id,
            "active": active,
        }
        if discovered is not None:
            msg["discovered"] = discovered
        if local_track_boxes is not None:
           msg["local_track_boxes"] = local_track_boxes
        if local_track_poses is not None:
            msg["local_track_poses"] = local_track_poses
        if interactions is not None:
            msg["interactions"] = interactions
        if feet_pos is not None:
            msg["feet_pos"] = feet_pos
        if face_embedding is not None:
            msg["face_embedding"] = face_embedding
        if bbox_embedding is not None:
            msg["bbox_embedding"] = bbox_embedding

        self._database_write('local_tracks', msg)


    def read_local_tracks(self, id=None):
        ret = self._database_read('local_tracks', id)
        parsed = ret.json()  
        return parsed

    def write_global_tracks(self, trackinfo):
        pass
    
    def read_global_tracks(self):
        ret = self._database_read('global_tracks', id)
        parsed = ret.json()  
        return parsed

    def write_interactions(self, interaction_alert, employee, customer, interaction_time=None):
        # TODO 
        msg = {
        }
        self._database_write('cameras', msg)

    def read_interactions(self):
        ret = self._database_read('interactions', id)
        parsed = ret.json()  
        return parsed


if __name__ == '__main__':
    # initialize a Skai Database Interface
    sdi = SkaiDatabaseInterface(verbose=True)

    """ testing flags """
    ### finished testing checklist ###
    # [x] 'alerts'
    # [x] 'cameras'
    # [x] 'boxes'
    # [x] 'poses'
    # [x] 'feet_positions'
    # [x] 'local_tracks'
    # [ ] 'global_tracks'
    # [ ] 'interactions'

    # testing list flags
    test_alerts = False
    test_cameras = True
    test_boxes = False
    test_poses = False
    test_feet_positions = False
    test_local_tracks = False
    test_global_tracks = False
    test_interactions = False

    # set true to only read (no writing)
    read_only = False
     
    """ bounding box write / read example """
    if test_boxes:
        # 3 people in frame example
        frame_bboxes = [[1, 111, 222, 20, 42], [2, 333, 444, 69, 42], [3, 555, 666, 24, 34]]
        # write bboxes found in a frame
        sdi.write_bboxes(frame_bboxes)
        # read from specific frame id (starts at 1)
        print(f'bbox frame id 4: {sdi.read_bboxes(id=4)}')
        # read all frame ids and their bboxes
        print(f'all frames all bboxes: {sdi.read_bboxes()}\n\n')
        
    """ pose write / read example """
    if test_poses:
        # 2 people in frame example (note: no tracking yet for pose)
        frame_poses = [[[1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7],
                        [8, 8], [9, 9], [10, 10], [11, 11], [12, 12], [13, 13],
                        [14, 14], [15, 15], [16, 16], [17, 17], [18, 18]],
                       [[1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7],
                        [8, 8], [9, 9], [10, 10], [11, 11], [12, 12], [13, 13],
                        [14, 14], [15, 15], [16, 16], [17, 17], [18, 18]]]
        if not read_only:
            sdi.write_poses(frame_poses)
        print(f'read poses id 1: {sdi.read_poses(id=1)}')
        print(f'read all poses: {sdi.read_poses()}')
        
    """ feet position write / read example """
    if test_feet_positions:
        feet_in_frame = [ [420, 69.2, 0], [120, 240, 0], [69, 69, 0] ]
        if not read_only:
            sdi.write_feet_positions(feet_in_frame)
        print(f'feet position id=1: {sdi.read_feet_positions(id=1)}')
        print(f'all feet positions: {sdi.read_feet_positions()}')
    
    """ test write cameras """
    if test_cameras:
        if not read_only:
            try:
                # sdi.update_camera()
                sdi.write_cameras(
                    mac_addr=12345678,
                    ip_address="1.1.1.1",
                    camera_matrix= { 'row1': 1, 'row2': 2},
                    dist_coef= { 'row1': 1, 'row2': 2}, # {1,2,3,4,5,6,7,8,9,10,11,12,13,14},
                    calib_resolution=[1, 2],
                    position={ 'row1': 1, 'row2': 2}, #{1, 2, 3},
                    quaternion={ 'row1': 1, 'row2': 2}, #{1, 2, 3, 4},
                    homography= { 'row1': 1, 'row2': 2}, #{{1, 2, 3}, {1, 2, 3}, {1, 2, 3}, {1, 2, 3}},
                    floor_eq={ 'row1': 1, 'row2': 2}, # {1, 2, 3, 4},
                    cam_to_floor={ 'row1': 1, 'row2': 2} # {{1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}})
                )
                ret = sdi.get_camera_by_mac_address(54321)
                result = ret.json()['results'][0]
                print(result)
                code.interact(local=locals())
                
                print(ret)
            except Exception as e:
                print(e)
        # print(f'camera id=1: {sdi.read_cameras(id=1)}')
        # print(f'all cameras: {sdi.read_cameras()}')
    
    """ test alerts """
    if test_alerts:
        if not read_only:
            sdi.write_alerts('some event')
        print(f'alert id=1: {sdi.read_alerts(id=1)}')
        print(f'all alerts: {sdi.read_alerts()}')

    """ test local tracks """
    if test_local_tracks:
        if not read_only:
            
            # first write camera, box, feet 3 times
            for i in range(3):
                sdi.write_cameras(
                    ip_address="1.1.1.1",
                    camera_matrix=[[1, 2, 3], [1, 2, 3], [1, 2, 3]],
                    dist_coef=[1,2,3,4,5,6,7,8,9,10,11,12,13,14],
                    calib_resolution=[1, 2],
                    position=[1, 2, 3],
                    quaternion=[1, 2, 3, 4],
                    homography=[[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3]],
                    floor_eq=[1, 2, 3, 4],
                    cam_to_floor=[[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]])
                frame_bboxes = [[1, 111, 222, 20, 42], [2, 333, 444, 69, 42], [3, 555, 666, 24, 34]]
                sdi.write_bboxes(frame_bboxes)
                feet_in_frame = [ [420, 69.2, 0], [120, 240, 0], [69, 69, 0] ]
                sdi.write_feet_positions(feet_in_frame)
            
            # # then related to that
            input('press enter to write id 2 to db')
            sdi.write_local_tracks(
                classification="EMP",
                camera_id=1,
                active=True,
                discovered=None, # assume now if None
                local_track_boxes=2,
                local_track_poses=None,
                interactions=None,
                feet_pos=2,
                face_embedding=np.arange(3).tolist(),
                bbox_embedding=np.arange(2).tolist()
            )
            input('press enter to write id 3 to db')
            sdi.write_local_tracks(
                classification="EMP",
                camera_id=1,
                active=True,
                discovered=None, # assume now if None
                local_track_boxes=3,
                local_track_poses=None,
                interactions=None,
                feet_pos=3,
                face_embedding=np.arange(3).tolist(),
                bbox_embedding=np.arange(2).tolist()
            )

        # print(f'local track id=1: {sdi.read_local_tracks(id=1)}')
        # print(f'all local tracks: {sdi.read_local_tracks()}')

    """ test interactions """
    if test_interactions:
        pass
