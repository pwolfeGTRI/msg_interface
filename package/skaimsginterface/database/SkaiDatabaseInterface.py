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


    #region global track endpoints
    def post_new_global_track(self, global_track_data):
        """
        Sends a POST request for a new global track with the provided json data.
        global_track_data : json
            Data for new global track
            {
                'time_discovered': 1657982174,
                'active': True,
                'classification': 3,
                'meta': {
                    "vehicle_meta_color": "yellow",
                    "vehicle_meta_type": "BMW",
                    "vehicle_meta_model": "X2 Sport"
                }
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/global_tracks/', data=json.dumps(global_track_data), headers=headers)).status_code

    def get_global_track_by_pk(self, pk):
        """
        Sends a GET request for a global track with the passed primary key.
        pk : int
            Primary key for global track to receive
        returns : Global track object as json
        """
        return (requests.get(f'{self.url}/global_tracks/{pk}')).json()

    def get_all_global_tracks(self):
        """
        Sends a GET request for all global tracks within the database.
        returns : Global track object(s) as json
        """
        return (requests.get(f'{self.url}/global_tracks/')).json()

    def delete_global_track_by_pk(self, pk):
        """
        Sends a DELETE request for a global track with the passed primary key.
        pk : int
            Primary key for global track to delete
        returns : Status code
        """
        return (requests.delete(f'{self.url}/global_tracks/{pk}')).status_code
    
    def update_global_track_time_discovered(self, pk, time_discovered):
        """
        Sends a POST request for updating the time discovered of the global track with the passed primary key.
        pk : int
            Primary key for global track to receive
        time_discovered : int
            Time discovered in unix time
        returns : Status code
        """
        return (requests.post(f'{self.url}/global_tracks/set_time_discovered/{pk}/{time_discovered}')).status_code

    def update_global_track_classification(self, pk, classification):
        """
        Sends a POST request for updating the classification of the global track with the passed primary key.
        pk : int
            Primary key for global track to receive
        classification : int or string
            Classification value that matches the CLASSIFICATION enum values
        returns : Status code
        """
        return (requests.post(f'{self.url}/global_tracks/set_classification/{pk}/{classification}')).status_code

    def update_global_track_meta(self, pk, meta):
        """
        Sends a POST request for updating the meta of the global track with the passed primary key.
        pk : int
            Primary key for global track to receive
        meta : json
            Meta data json with a structure like 
            { 
                'meta': {
                    'vehicle_meta_color': 'gray',
                    'vehicle_meta_type': 'BMW',
                    'etc': 'etc'
                }
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/global_tracks/set_meta/{pk}', data=json.dumps(meta), headers=headers)).status_code
 
    def get_global_tracks_by_filter(self, gt_filter):
        """
        Sends a GET request for all global tracks within the database that match the provided filter.
        gt_filter : json
            Global track filter json with a structure like 
            {
                'time_discovered': [1657982174, 1659982174],
                'classification': 3,
                'meta': {
                    "vehicle_meta_color": "yellow",
                    "vehicle_meta_type": "BMW",
                    "vehicle_meta_model": "X2 Sport"
                }
            }
        returns : Global track object(s) that match the parameters of the filter as json
        note: objects returned will be within the time_discovered range, have the exact classification passed, and will match at least one of the meta properties provided
        """
        headers = {'Content-type': 'application/json'}
        return (requests.get(f'{self.url}/global_tracks/get_by_filter', data=json.dumps(gt_filter), headers=headers)).json()
    #endregion

    #region vehicle person association endpoints
    def post_new_vehicle_person_association(self, vehicle_person_association_data):
        """
        Sends a POST request for a new vehicle person association with the provided json data.
        vehicle_person_association_data : json
            Data for new vehicle person association with structure like
            {
                'car_global_track': 2,
                'person_global_track': 1,
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/vehicle_person_associations/', data=json.dumps(vehicle_person_association_data), headers=headers)).status_code

    def get_vehicle_person_association_by_pk(self, pk):
        """
        Sends a GET request for a vehicle person association with the passed primary key.
        pk : int
            Primary key for vehicle person association to receive
        returns : Vehicle Person Association object as json
        """
        return (requests.get(f'{self.url}/vehicle_person_associations/{pk}')).json()

    def get_all_vehicle_person_associations(self):
        """
        Sends a GET request for all vehicle person associations within the database.
        returns : Vehicle Person Association(s) as json
        """
        return (requests.get(f'{self.url}/vehicle_person_associations/')).json()

    def delete_vehicle_person_association_by_pk(self, pk):
        """
        Sends a DELETE request for a vehicle person association with the passed primary key.
        pk : int
            Primary key for vehicle person association to delete
        returns : Status code
        """
        return (requests.delete(f'{self.url}/vehicle_person_associations/{pk}')).status_code
    #endregion

    #region camera endpoints
    def post_new_camera(self, camera_data):
        """
        Sends a POST request for a new camera with the provided json data.
        camera_data : json
            Data for new camera with structure like
            {
                'mac_address': 'ec:71:db:23:10:c6',
                'ip_address': '192.168.0.2',
                'stream_uri': 'rtsp://admin:reolink@192.168.0.2//h264Preview_01_main',
                'name': 'somename'
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/cameras/', data=json.dumps(camera_data), headers=headers)).status_code

    def get_camera_by_pk(self, pk):
        """
        Sends a GET request for a camera with the passed primary key.
        pk : int
            Primary key for camera to receive
        returns : Camera object as json
        """
        return (requests.get(f'{self.url}/cameras/{pk}')).json()

    def get_all_cameras(self):
        """
        Sends a GET request for all cameras within the database.
        returns : Camera object(s) as json
        """
        return (requests.get(f'{self.url}/cameras/')).json()

    def delete_camera_by_pk(self, pk):
        """
        Sends a DELETE request for a camera with the passed primary key.
        pk : int
            Primary key for camera to delete
        returns : Status code
        """
        return (requests.delete(f'{self.url}/cameras/{pk}')).status_code
    
    def update_camera_calibration_details(self, mac_address, calibration_json):
        """
        Sends a POST request for updating the calibration details of the camera with the passed mac address.
        mac_address : int
            mac address of camera to receive
        calibration_json : json
            Calibration details in json format with a structure like 
            { 
                "orig_res": [2304, 1296],
                "cam_matrix": [[1872.613708968491, 0.0, 1355.138486070091], [0.0, 1896.4422463362916, 909.4201602392025], [0.0, 0.0, 1.0]], 
                "dist_coeff": [[-0.6362982432948103, 0.7439771281850569, -5.324631009757216e-05, -0.0014847892764532215, 0.034204522443160634, -0.30451667904984236, 0.5344090826454042, 0.28124529498282147, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], 
                "cam_pose": [[-0.2643004595381173, -0.3784993418146447, 0.8870645496996376, 0.6856852374803691], [-0.9643401559717386, 0.11697557082609789, -0.2374126774422785, 6.15587791992814], [-0.013904339910355524, -0.9181802459625177, -0.395918811444806, 2.1189910164597197], [0.0, 0.0, 0.0, 1.0]], 
                "plane_eq": [0.013904339910351924, 0.9181802459625168, 0.3959188114448081, -2.118991016459728]
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/cameras/set_calibration_details/{mac_address}', data=json.dumps(calibration_json), headers=headers)).status_code

    def update_camera_connection_details(self, mac_address, connection_json):
        """
        Sends a POST request for updating the connection details of the camera with the passed mac address.
        mac_address : int
            mac address of camera to receive
        connection_json : json
            Connection details in json format with a structure like 
            { 
                "ip_address": "192.168.0.3",
                "stream_uri": "rtsp://admin:reolink@192.168.0.3//h264Preview_01_main",
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/cameras/set_calibration_details/{mac_address}', data=json.dumps(connection_json), headers=headers)).status_code

    def update_camera_processing_group(self, mac_address, group_json):
        """
        Sends a POST request for updating the processing group of the camera with the passed mac address.
        mac_address : int
            mac address of camera to receive
        group_json : json
            Processing group details in json format with a structure like 
            { 
                "processing_group": 0
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/cameras/set_processing_group/{mac_address}', data=json.dumps(group_json), headers=headers)).status_code

    def get_camera_by_mac_address(self, mac_address):
        """
        Sends a GET request for the camera with the specified mac address.
        returns : Camera object as json
        """
        return (requests.get(f'{self.url}/cameras/get_by_mac_address/{mac_address}')).json()

    def get_camera_by_processing_group(self, processing_group):
        """
        Sends a GET request for the camera(s) with the specified processing group.
        returns : Camera object(s) as json
        """
        return (requests.get(f'{self.url}/cameras/get_by_processing_group/{processing_group}')).json()

    def get_camera_by_name(self, name):
        """
        Sends a GET request for the camera with the specified name.
        returns : Camera object(s) as json
        """
        return (requests.get(f'{self.url}/cameras/get_by_name/{name}')).json()

    # need to add deletes for cameras but want to talk to nathan about redoing the endpoints for them
    #endregion

    #region location history endpoints
    def post_new_location_history(self, location_history_data):
        """
        Sends a POST request for a new location history with the provided json data.
        location_history_data : json
            Data for new location history with structure like
            {
                'globaltrack_id': 0,
                'mac_address': 0,
                'timestamp': 1657982174,
                'x': 1.0,
                'y': 1.0,
                'z': 1.0,
                'location_type': 0
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/location_histories/', data=json.dumps(location_history_data), headers=headers)).status_code

    def get_location_histories_by_pk(self, pk):
        """
        Sends a GET request for a location history with the passed primary key.
        pk : int
            Primary key for location history to receive
        returns : Location History object as json
        """
        return (requests.get(f'{self.url}/location_histories/{pk}')).json()

    def get_all_location_histories(self):
        """
        Sends a GET request for all location histories within the database.
        returns : Location history object(s) as json
        """
        return (requests.get(f'{self.url}/location_histories/')).json()

    def delete_location_history_by_pk(self, pk):
        """
        Sends a DELETE request for a location history with the passed primary key.
        pk : int
            Primary key for location history to delete
        returns : Status code
        """
        return (requests.delete(f'{self.url}/location_histories/{pk}')).status_code
    #endregion

    #region face embedding endpoints
    def post_new_face_embedding(self, face_embedding_data):
        """
        Sends a POST request for a new face embedding with the provided json data.
        face_embedding_data : json
            Data for new face embedding with structure like
            {
                'globaltrack_id': 1,
                'vals': {},
                'box': {},
                'timestamp': 1657982174,
                'mac_address': 0,
                'confidence': 1.0
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/face_embeddings/', data=json.dumps(face_embedding_data), headers=headers)).status_code

    def get_face_embedding_by_pk(self, pk):
        """
        Sends a GET request for a face embedding with the passed primary key.
        pk : int
            Primary key for face embedding to receive
        returns : Faceembedding object as json
        """
        return (requests.get(f'{self.url}/face_embeddings/{pk}')).json()

    def get_all_face_embeddings(self):
        """
        Sends a GET request for all face embeddings within the database.
        returns : Face embedding object(s) as json
        """
        return (requests.get(f'{self.url}/face_embeddings/')).json()

    def delete_face_embedding_by_pk(self, pk):
        """
        Sends a DELETE request for a face embedding with the passed primary key.
        pk : int
            Primary key for face embedding to delete
        returns : Status code
        """
        return (requests.delete(f'{self.url}/face_embeddings/{pk}')).status_code

    def get_face_embeddings_by_global_track(self, global_track_id):
        """
        Sends a GET request for the face embeddings associated with the specified global track.
        returns : Face embedding object(s) as json
        """
        return (requests.get(f'{self.url}/face_embeddings/get_by_global_track/{global_track_id}')).json()

    def update_face_embeddings_by_global_track(self, global_track_id, embedding_json):
        """
        Sends a POST request for updating the face embedding(s) of the global track with the passed primary key.
        global_track_id : int
            Primary key of global track to receive
        embedding_json: json
            Face embedding json with a structure like 
            {
                'data': [
                    {
                        'vals': {},
                        'box': {},
                        'timestamp': 1657000000,
                        'mac_address': 0,
                        'confidence': 1
                    },
                    {
                        'vals': {},
                        'box': {},
                        'timestamp': 1657000000,
                        'mac_address': 0,
                        'confidence': 1
                    },   
                    {
                        'vals': {},
                        'box': {},
                        'timestamp': 1657000000,
                        'mac_address': 0,
                        'confidence': 1
                    },   
                    {
                        'vals': {},
                        'box': {},
                        'timestamp': 1657000000,
                        'mac_address': 0,
                        'confidence': 1
                    },   
                    {
                        'vals': {},
                        'box': {},
                        'timestamp': 1657000000,
                        'mac_address': 0,
                        'confidence': 1
                    }
                ]
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/face_embeddings/post_by_global_track/{global_track_id}', data=json.dumps(embedding_json), headers=headers)).status_code
    #endregion

    #region bbox embedding endpoints
    def post_new_bbox_embedding(self, bbox_embedding_data):
        """
        Sends a POST request for a new bbox embedding with the provided json data.
        bbox_embedding_data : json
            Data for new bbox embedding with structure like
            {
                'globaltrack_id': 1,
                'vals': {},
                'box': {},
                'timestamp': 1657982174,
                'mac_address': 0,
                'confidence': 1.0
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/bbox_embeddings/', data=json.dumps(bbox_embedding_data), headers=headers)).status_code

    def get_bbox_embedding_by_pk(self, pk):
        """
        Sends a GET request for a bbox embedding with the passed primary key.
        pk : int
            Primary key for bbox embedding to receive
        returns : Bbox embedding object as json
        """
        return (requests.get(f'{self.url}/bbox_embeddings/{pk}')).json()

    def get_all_bbox_embeddings(self):
        """
        Sends a GET request for all bbox embeddings within the database.
        returns : Bbox embedding object(s) as json
        """
        return (requests.get(f'{self.url}/bbox_embeddings/')).json()

    def delete_bbox_embedding_by_pk(self, pk):
        """
        Sends a DELETE request for a bbox embedding with the passed primary key.
        pk : int
            Primary key for bbox embedding to delete
        returns : Status code
        """
        return (requests.delete(f'{self.url}/bbox_embeddings/{pk}')).status_code

    def get_bbox_embeddings_by_global_track(self, global_track_id):
        """
        Sends a GET request for the bbox embeddings associated with the specified global track.
        returns : Bbox embedding object(s) as json
        """
        return (requests.get(f'{self.url}/bbox_embeddings/get_by_global_track/{global_track_id}')).json()

    def update_bbox_embeddings_by_global_track(self, global_track_id, embedding_json):
        """
        Sends a POST request for updating the bbox embedding(s) of the global track with the passed primary key.
        global_track_id : int
            Primary key of global track to receive
        embedding_json: json
            Bbox embedding json with a structure like 
            {
                'data': [
                    {
                        'vals': {},
                        'box': {},
                        'timestamp': 1657000000,
                        'mac_address': 0,
                        'confidence': 1
                    },
                    {
                        'vals': {},
                        'box': {},
                        'timestamp': 1657000000,
                        'mac_address': 0,
                        'confidence': 1
                    },   
                    {
                        'vals': {},
                        'box': {},
                        'timestamp': 1657000000,
                        'mac_address': 0,
                        'confidence': 1
                    },   
                    {
                        'vals': {},
                        'box': {},
                        'timestamp': 1657000000,
                        'mac_address': 0,
                        'confidence': 1
                    },   
                    {
                        'vals': {},
                        'box': {},
                        'timestamp': 1657000000,
                        'mac_address': 0,
                        'confidence': 1
                    }
                ]
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/bbox_embeddings/post_by_global_track/{global_track_id}', data=json.dumps(embedding_json), headers=headers)).status_code
    #endregion

    #region license plate endpoints
    def post_new_license_plate(self, license_plate_data):
        """
        Sends a POST request for a new license plate with the provided json data.
        license_plate_data : json
            Data for new license plate with structure like
            {
                'globaltrack_id': 1,
                'vals': {},
                'box': {},
                'timestamp': 1657982174,
                'mac_address': 0,
                'confidence': 1.0
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/license_plates/', data=json.dumps(license_plate_data), headers=headers)).status_code

    def get_license_plate_by_pk(self, pk):
        """
        Sends a GET request for a license plate with the passed primary key.
        pk : int
            Primary key for license plate to receive
        returns : License plate object as json
        """
        return (requests.get(f'{self.url}/license_plates/{pk}')).json()

    def get_all_license_plates(self):
        """
        Sends a GET request for all license plates within the database.
        returns : License plate object(s) as json
        """
        return (requests.get(f'{self.url}/license_plates/')).json()

    def delete_license_plate_by_pk(self, pk):
        """
        Sends a DELETE request for a license plate with the passed primary key.
        pk : int
            Primary key for license plate to delete
        returns : Status code
        """
        return (requests.delete(f'{self.url}/license_plates/{pk}')).status_code

    def get_license_plates_by_global_track(self, global_track_id):
        """
        Sends a GET request for the license plates associated with the specified global track.
        returns : License plate object(s) as json
        """
        return (requests.get(f'{self.url}/license_plates/get_by_global_track/{global_track_id}')).json()

    def update_license_plates_by_global_track(self, global_track_id, license_json):
        """
        Sends a POST request for updating the license plate(s) of the global track with the passed primary key.
        global_track_id : int
            Primary key of global track to receive
        license_json: json
            license plate json with a structure like 
            {
                'data': [
                    {
                        'vals': {},
                        'box': {},
                        'timestamp': 1657000000,
                        'mac_address': 0,
                        'confidence': 1
                    },
                    {
                        'vals': {},
                        'box': {},
                        'timestamp': 1657000000,
                        'mac_address': 0,
                        'confidence': 1
                    },   
                    {
                        'vals': {},
                        'box': {},
                        'timestamp': 1657000000,
                        'mac_address': 0,
                        'confidence': 1
                    },   
                    {
                        'vals': {},
                        'box': {},
                        'timestamp': 1657000000,
                        'mac_address': 0,
                        'confidence': 1
                    },   
                    {
                        'vals': {},
                        'box': {},
                        'timestamp': 1657000000,
                        'mac_address': 0,
                        'confidence': 1
                    }
                ]
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/license_plates/post_by_global_track/{global_track_id}', data=json.dumps(license_json), headers=headers)).status_code
    #endregion

    #region event endpoints
    def post_new_event(self, event_data):
        """
        Sends a POST request for a new event with the provided json data.
        event_data : json
            Data for new event with structure like
            {
                'event_type': 0,
                'start_timestamp': 1657000000,
                'end_timestamp': 1657000010,
                'confidence': 1.0
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/events/', data=json.dumps(event_data), headers=headers)).status_code

    def get_event_by_pk(self, pk):
        """
        Sends a GET request for an event with the passed primary key.
        pk : int
            Primary key for event to receive
        returns : Event object as json
        """
        return (requests.get(f'{self.url}/events/{pk}')).json()

    def get_all_events(self):
        """
        Sends a GET request for all events within the database.
        returns : Event object(s) as json
        """
        return (requests.get(f'{self.url}/events/')).json()

    def delete_event_by_pk(self, pk):
        """
        Sends a DELETE request for an event with the passed primary key.
        pk : int
            Primary key for event to delete
        returns : Status code
        """
        return (requests.delete(f'{self.url}/events/{pk}')).status_code
    
    def get_event_by_location(self, location):
        """
        Sends a GET request for the event(s) associated with the specified location.
        returns : Event object(s) as json
        """
        return (requests.get(f'{self.url}/events/get_by_location_type/{location}')).json()
    #endregion

    #region location endpoints
    def post_new_location(self, location_data):
        """
        Sends a POST request for a new location with the provided json data.
        location_data : json
            Data for new location with structure like
            {
                'event_id': 1,
                'x': 1.0,
                'y': 1.0,
                'z': 1.0,
                'error': 1.0,
                'location_type': 'some location'
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/locations/', data=json.dumps(location_data), headers=headers)).status_code

    def get_location_by_pk(self, pk):
        """
        Sends a GET request for a location with the passed primary key.
        pk : int
            Primary key for location to receive
        returns : Location object as json
        """
        return (requests.get(f'{self.url}/locations/{pk}')).json()

    def get_all_locations(self):
        """
        Sends a GET request for all locations within the database.
        returns : Location object(s) as json
        """
        return (requests.get(f'{self.url}/locations/')).json()

    def delete_location_by_pk(self, pk):
        """
        Sends a DELETE request for a location with the passed primary key.
        pk : int
            Primary key for location to delete
        returns : Status code
        """
        return (requests.delete(f'{self.url}/locations/{pk}')).status_code
    #endregion

    #region primary global tracks in event endpoints
    def post_new_primary_global_tracks_in_event(self, primary_global_tracks_in_event_data):
        """
        Sends a POST request for a new primary global track in event with the provided json data.
        primary_global_tracks_in_event_data : json
            Data for new primary global track in event with structure like
            {
                'global_track_id': 1,
                'event_id': 1,
                'confidence': 1.0
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/primary_global_tracks_in_events/', data=json.dumps(primary_global_tracks_in_event_data), headers=headers)).status_code

    def get_primary_global_tracks_in_event_by_pk(self, pk):
        """
        Sends a GET request for a primary global tracks in event with the passed primary key.
        pk : int
            Primary key for primary global tracks in event to receive
        returns : Primary global tracks in event object as json
        """
        return (requests.get(f'{self.url}/primary_global_tracks_in_events/{pk}')).json()

    def get_all_primary_global_tracks_in_events(self):
        """
        Sends a GET request for all primary global tracks in events within the database.
        returns : Primary global tracks in event object(s) as json
        """
        return (requests.get(f'{self.url}/primary_global_tracks_in_events/')).json()

    def delete_primary_global_tracks_in_event_by_pk(self, pk):
        """
        Sends a DELETE request for a primary global tracks in event with the passed primary key.
        pk : int
            Primary key for primary global tracks in event to delete
        returns : Status code
        """
        return (requests.delete(f'{self.url}/primary_global_tracks_in_events/{pk}')).status_code
    #endregion

    #region supporting global tracks in event endpoints
    def post_new_supporting_global_tracks_in_event(self, supporting_global_tracks_in_event_data):
        """
        Sends a POST request for a new supporting global track in event with the provided json data.
        supporting_global_tracks_in_event_data : json
            Data for new supporting global track in event with structure like
            {
                'global_track_id': 1,
                'event_id': 1,
                'confidence': 1.0
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/supporting_global_tracks_in_events/', data=json.dumps(supporting_global_tracks_in_event_data), headers=headers)).status_code

    def get_supporting_global_tracks_in_event_by_pk(self, pk):
        """
        Sends a GET request for a supporting global tracks in event with the passed primary key.
        pk : int
            Primary key for supporting global tracks in event to receive
        returns : Supporting global tracks in event object as json
        """
        return (requests.get(f'{self.url}/supporting_global_tracks_in_events/{pk}')).json()

    def get_all_supporting_global_tracks_in_events(self):
        """
        Sends a GET request for all supporting global tracks in events within the database.
        returns : Supporting global tracks in event object(s) as json
        """
        return (requests.get(f'{self.url}/supporting_global_tracks_in_events/')).json()

    def delete_supporting_global_tracks_in_event_by_pk(self, pk):
        """
        Sends a DELETE request for a supporting global track in event with the passed primary key.
        pk : int
            Primary key for supporting global track in event to delete
        returns : Status code
        """
        return (requests.delete(f'{self.url}/supporting_global_tracks_in_events/{pk}')).status_code
    #endregion
    
    #region camera event endpoints
    def post_new_camera_event(self, camera_event_data):
        """
        Sends a POST request for a new camera event with the provided json data.
        camera_event_data : json
            Data for new camera event with structure like
            {
                'camera_id': 1,
                'event_id': 1,
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/camera_events/', data=json.dumps(camera_event_data), headers=headers)).status_code

    def get_camera_event_by_pk(self, pk):
        """
        Sends a GET request for a camera event with the passed primary key.
        pk : int
            Primary key for camera event to receive
        returns : Camera event object as json
        """
        return (requests.get(f'{self.url}/camera_events/{pk}')).json()

    def get_all_camera_events(self):
        """
        Sends a GET request for all camera events within the database.
        returns : Camera event object(s) as json
        """
        return (requests.get(f'{self.url}/camera_events/')).json()

    def delete_camera_event_by_pk(self, pk):
        """
        Sends a DELETE request for a camera event with the passed primary key.
        pk : int
            Primary key for camera event to delete
        returns : Status code
        """
        return (requests.delete(f'{self.url}/camera_events/{pk}')).status_code
    #endregion

    #region camera event endpoints
    def post_new_marker(self, marker_data):
        """
        Sends a POST request for a new marker with the provided json data.
        marker_data : json
            Data for new marker with structure like
            {
                'name': 'name1',
                'x': 0,
                'y': 1,
                'z': 2
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/markers/', data=json.dumps(marker_data), headers=headers)).status_code

    def get_marker_by_pk(self, pk):
        """
        Sends a GET request for a marker with the passed primary key.
        pk : int
            Primary key for marker to receive
        returns : Marker object as json
        """
        return (requests.get(f'{self.url}/markers/{pk}')).json()

    def get_all_markers(self):
        """
        Sends a GET request for all markers within the database.
        returns : Marker object(s) as json
        """
        return (requests.get(f'{self.url}/markers/')).json()

    def delete_marker_by_pk(self, pk):
        """
        Sends a DELETE request for a marker with the passed primary key.
        pk : int
            Primary key for marker to delete
        returns : Status code
        """
        return (requests.delete(f'{self.url}/markers/{pk}')).status_code

    def get_marker_by_name(self, name):
        """
        Sends a GET request for the marker with the specified name.
        returns : Marker object as json
        """
        return (requests.get(f'{self.url}/markers/get_by_name/{name}')).json()
    
    def update_marker_name_by_id(self, pk, name):
        """
        Sends a POST request for updating the name of the marker with the passed primary key.
        pk : int
            Primary key for marker to receive
        name : string
            New name to be set to marker
        returns : Status code
        """
        return (requests.post(f'{self.url}/markers/set_new_name_by_id/{pk}/{name}')).status_code

    def update_marker_name(self, old_name, new_name):
        """
        Sends a POST request for updating the name of the marker with the passed old name.
        old_name: string
            Old name of marker to receive
        new_name : string
            New name to be set to marker
        returns : Status code
        """
        return (requests.post(f'{self.url}/markers/set_new_name/{old_name}/{new_name}')).status_code

    def update_marker_pose_by_id(self, pk, pose_json):
        """
        Sends a POST request for updating the pose of the marker with the passed primary key.
        pk : int
            primary key of marker to receive
        pose_json : json
            Pose info in json format with a structure like 
            { 
                "x": 1,
                "y": 2, 
                "z": 3
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/markers/set_pose_by_id/{pk}', data=json.dumps(pose_json), headers=headers)).status_code

    def update_marker_pose_by_name(self, name, pose_json):
        """
        Sends a POST request for updating the pose of the marker with the passed name.
        name : string
            name of marker to receive
        pose_json : json
            Pose info in json format with a structure like 
            { 
                "x": 1,
                "y": 2, 
                "z": 3
            }
        returns : Status code
        """
        headers = {'Content-type': 'application/json'}
        return (requests.post(f'{self.url}/markers/set_pose/{name}', data=json.dumps(pose_json), headers=headers)).status_code
    #endregion


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
