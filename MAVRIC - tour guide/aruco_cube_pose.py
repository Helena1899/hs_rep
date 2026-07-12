#!/usr/bin/env python3
import numpy as np
import cv2
import cv2.aruco as aruco
import rospy
import tf
from sensor_msgs.msg import CameraInfo, Image
from cv_bridge import CvBridge


class ArUcoHeadDetector:
    def __init__(self, name, image_topic, camera_info_topic, frame_id):
        self.name = name
        self.image_topic = image_topic
        self.camera_info_topic = camera_info_topic
        self.frame_id = frame_id

        # ArUco cube configuration
        self.marker_size = 0.095 + 0.005  # Size of one marker in meters
        self.cube_to_head_offset = np.array([-0.3, 0, 0.1])  # Offset from cube center to head

        # Define the ArUco dictionary and board
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_1000)
        c_pt = self.marker_size / 2

        # Marker corners and IDs (6-sided cube)
        board_ids = np.array([[0], [1], [2], [3], [4], [5]], dtype=np.int32)
        board_corners = [
            np.array([[-c_pt, c_pt, c_pt], [c_pt, c_pt, c_pt], [c_pt, -c_pt, c_pt], [-c_pt, -c_pt, c_pt]], dtype=np.float32),
            np.array([[-c_pt, -c_pt, c_pt], [c_pt, -c_pt, c_pt], [c_pt, -c_pt, -c_pt], [-c_pt, -c_pt, -c_pt]], dtype=np.float32),
            np.array([[-c_pt, c_pt, c_pt], [-c_pt, -c_pt, c_pt], [-c_pt, -c_pt, -c_pt], [-c_pt, c_pt, -c_pt]], dtype=np.float32),
            np.array([[c_pt, c_pt, c_pt], [-c_pt, c_pt, c_pt], [-c_pt, c_pt, -c_pt], [c_pt, c_pt, -c_pt]], dtype=np.float32),
            np.array([[c_pt, -c_pt, c_pt], [c_pt, c_pt, c_pt], [c_pt, c_pt, -c_pt], [c_pt, -c_pt, -c_pt]], dtype=np.float32),
            np.array([[-c_pt, -c_pt, -c_pt], [c_pt, -c_pt, -c_pt], [c_pt, c_pt, -c_pt], [-c_pt, c_pt, -c_pt]], dtype=np.float32)
        ]
        self.board = aruco.Board(board_corners, self.aruco_dict, board_ids)

        # Camera calibration
        self.camera_matrix = None
        self.dist_coeffs = None

        # ROS tools
        self.bridge = CvBridge()
        self.tf_broadcaster = tf.TransformBroadcaster()

        # Subscribers
        self.image_sub = rospy.Subscriber(self.image_topic, Image, self.image_callback, queue_size=1)
        self.camera_info_sub = rospy.Subscriber(self.camera_info_topic, CameraInfo, self.camera_info_callback)

    def camera_info_callback(self, msg):
        self.camera_matrix = np.array(msg.K).reshape((3, 3))
        self.dist_coeffs = np.array(msg.D)

    def image_callback(self, msg):
        if self.camera_matrix is None or self.dist_coeffs is None:
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            rospy.logwarn(f"[{self.name}] Failed to convert image: {e}")
            return

        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = aruco.detectMarkers(gray, self.aruco_dict)

        # Check that markers were detected
        if ids is None or len(ids) == 0:
            rospy.loginfo(f"[{self.name}] No ArUco markers detected.")
            return

        retval, rvec, tvec = aruco.estimatePoseBoard(
            corners, ids, self.board,
            self.camera_matrix, self.dist_coeffs,
            np.empty((1, 3)), np.empty((1, 3))
        )

        if retval > 0:
            # Convert to quaternion
            R, _ = cv2.Rodrigues(rvec)
            T = np.eye(4)
            T[:3, :3] = R
            quaternion = tf.transformations.quaternion_from_matrix(T)

            # Adjust translation to head position
            head_position = R.dot(self.cube_to_head_offset) + tvec.flatten()

            # Broadcast the head TF
            self.tf_broadcaster.sendTransform(
                head_position,
                quaternion,
                rospy.Time.now(),
                f"{self.name}_head_pos",
                self.frame_id
            )

            rospy.loginfo(f"[{self.name}] Head detected at {head_position.round(3)}")
        else:
            rospy.loginfo(f"[{self.name}] Pose estimation failed.")


if __name__ == "__main__":
    rospy.init_node("multi_camera_aruco_head_tracker")

    # Start detectors for both cameras
    hsrb_cam = ArUcoHeadDetector(
        name="hsrb",
        image_topic="/hsrb/head_rgbd_sensor/rgb/image_raw",
        camera_info_topic="/hsrb/head_rgbd_sensor/rgb/camera_info",
        frame_id="head_rgbd_sensor_link"
    )

    d435_cam = ArUcoHeadDetector(
        name="d435i",
        image_topic="/d435i/color/image_raw",
        camera_info_topic="/d435i/depth/camera_info",
        frame_id="d435i_link"
    )

    rospy.spin()