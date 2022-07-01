#include <stdint.h>
#include <iostream>
#include <chrono>
#include "SkaimotProtoMsg.pb.h"
#include "PoseProtoMsg.pb.h"
#include "FeetPosProtoMsg.pb.h"


// base class
class SkaiMsg {
public:
  enum MsgType { UNKNOWN = 0, SKAIMOT = 1, POSE = 2, FEETPOS = 3 };

  // required member variables
  MsgType msg_type = UNKNOWN;
  SkaiMsg *proto_msg_class = nullptr;

  uint8_t *pack() {
    uint8_t *buffer;
    return nullptr;
  }

  void *unpack(uint8_t *msg_bytes) {}

private:
};

// class SkaimotMsg : public SkaiMsg {
// public:
//   void set_bbox(person, tlbr) {}
//   void set_face_embed(person, face_embed) {}
//   void set_bbox_embed(person, bbox_embed) {}
// };

// class PoseMsg : public SkaiMsg {
// public:
//   void set_keypoints(person, keypoints) {}
//   void set_xy(keypoint, xy) {}
// };

// class FeetPosMsg : public SkaiMsg {
// public:
//   void set_feet_pos(person, xyz) {}
// }


// void unpack_and_print_cam_id_and_timestamp_per_frame() {
// }

uint64_t get_current_timestamp() {
  using namespace std::chrono;
  uint64_t ms = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
  return ms;

}

int main() {
  bool test_skaimot = true;
  bool test_pose = false;
  bool test_feetpos = false;

  // test with 2 people, 5 cameras in camera group 
  uint8_t num_people = 2;
  uint8_t num_cams = 5;

  // generate some example camera id numbers
  // camera_id_macs = {}  
  // camera_id_nums = {}

  uint64_t ts = (uint64_t) (get_current_timestamp() * 1e9);

  if (test_skaimot) {
    printf("testing skaimot...\n");
    skaimsg::skaimot::SkaimotProtoMsg msg;
    // msg.add_camera_frames()

  }
  if (test_pose) {
    printf("testing pose...\n");
  }
  if (test_feetpos) {
    printf("testing feetpos...\n");
  }

}