#!/usr/bin/env python3
import numpy as np
import cv2
import cv2.aruco as aruco
import rospy
import tf
from sensor_msgs.msg import CameraInfo, Image
from std_msgs.msg import Bool, Float64, String
from cv_bridge import CvBridge
import time


class ArUcoHeadDetector:
    def __init__(self, name, image_topic, camera_info_topic, frame_id):
        self.name = name
        self.image_topic = image_topic
        self.camera_info_topic = camera_info_topic
        self.frame_id = frame_id
        self.int_head_prompt = 0

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

        # OpenCV's aruco.Board API changed in different versions.
        # For OpenCV 3.x and 4.x, use aruco.Board_create if aruco.Board is not available.
        if hasattr(aruco, "Board"):
            self.board = aruco.Board(board_corners, self.aruco_dict, board_ids)
        else:
            self.board = aruco.Board_create(board_corners, self.aruco_dict, board_ids)

        #self.board = aruco.Board(board_corners, self.aruco_dict, board_ids)

        # Camera calibration
        self.camera_matrix = None
        self.dist_coeffs = None

        # ROS tools
        self.bridge = CvBridge()
        self.tf_broadcaster = tf.TransformBroadcaster()

        # Subscribers
        self.image_sub = rospy.Subscriber(self.image_topic, Image, self.image_callback, queue_size=1)
        self.camera_info_sub = rospy.Subscriber(self.camera_info_topic, CameraInfo, self.camera_info_callback)

        # Additional variables for reaction detection and timing
        self.robot_tour_head_reaction_sub = rospy.Subscriber("/robot_tour/head_prompt", Bool, self.reaction_callback)
        self.reaction_time_pub = rospy.Publisher("/robot_tour/head_reaction_time", String, queue_size=10)

        self.pub_head_status = rospy.Publisher('/robot_tour/head_reaction_status', String, queue_size=10)


        self.reaction_active = False
        self.last_rvec = None
        self.start_time = None

    def camera_info_callback(self, msg):
        self.camera_matrix = np.array(msg.K).reshape((3, 3))
        self.dist_coeffs = np.array(msg.D)

    def reaction_callback(self, msg):
        """ Callback to activate/deactivate reaction detection """
        rospy.loginfo(f"[{self.name}] Waiting for /robot_tour/head_prompt topic to activate reaction detection.")
        self.reaction_active = msg.data
        self.start_time = time.time()  # Start timer when reaction is true
        self.pub_head_status.publish("Head Reaction Prompt_" + str(self.int_head_prompt))
        self.int_head_prompt += 1
        rospy.loginfo(f"[{self.name}] Reaction detection started.")


    def image_callback(self, msg):
        if self.camera_matrix is None or self.dist_coeffs is None:
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            rospy.logwarn_once(f"[{self.name}] Failed to convert image: {e}")
            return

        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = aruco.detectMarkers(gray, self.aruco_dict)

        # Check that markers were detected
        if ids is None or len(ids) == 0:
            # rospy.logwarn_once(f"[{self.name}] No ArUco markers detected.")
            return

        retval, rvec, tvec = aruco.estimatePoseBoard(
            corners, ids, self.board,
            self.camera_matrix, self.dist_coeffs,
            np.empty((1, 3)), np.empty((1, 3))
        )

        if retval > 0:

            # Compute head position in camera frame
            R, _ = cv2.Rodrigues(rvec)
            head_pos_cam = tvec.reshape(3) + R @ self.cube_to_head_offset

            # # Publish TF from camera frame to head (relative to /map)
            # self.tf_broadcaster.sendTransform(
            #     head_pos_cam,
            #     tf.transformations.quaternion_from_matrix(
            #         np.vstack((np.hstack((R, np.array([[0], [0], [0]]))), [0, 0, 0, 1]))
            #     ),
            #     rospy.Time.now(),
            #     "head_pos",
            #     self.frame_id
            # )


            # Compare yaw rotation with the previous one to check for ~180-degree rotation
            R, _ = cv2.Rodrigues(rvec)
            sy = np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)
            singular = sy < 1e-6

            if not singular:
                roll = np.arctan2(R[2, 1], R[2, 2])
                pitch = np.arctan2(-R[2, 0], sy)
                yaw = np.arctan2(R[1, 0], R[0, 0])
            else:
                roll = np.arctan2(-R[1, 2], R[1, 1])
                pitch = np.arctan2(-R[2, 0], sy)
                yaw = 0

            
            #print("1111111111111111111")
            #print(pitch, roll, yaw)
            
            if self.reaction_active:
                if time.time() - self.start_time > 30:  # Check if within 30 seconds
                    self.reaction_time_pub.publish("HeadPrompt_" + str(self.int_head_prompt)+"_ReactionTime_30")
                    self.pub_head_status.publish("HeadReaction Finished")
                    self.reaction_active = False
                    self.initial_roll = None
                    rospy.sleep(1)
                else:
                    # Save initial roll when reaction is first activated
                    if not hasattr(self, 'initial_roll') or self.initial_roll is None:
                        self.initial_roll = roll
                        #rospy.loginfo(f"[{self.name}] Initial roll saved: {np.rad2deg(self.initial_roll):.2f} deg")
                    else:
                        # Measure roll rotation
                        roll_diff = np.abs((roll - self.initial_roll + np.pi) % (2 * np.pi) - np.pi)
                        #print(self.initial_roll, roll_diff)

                        if np.deg2rad(180-90) < roll_diff < np.deg2rad(180+90) :  # About 180 degrees
                            elapsed_time = time.time() - self.start_time
                            self.reaction_time_pub.publish("HeadPrompt_" + str(self.int_head_prompt)+"_ReactionTime_"+str(elapsed_time))
                            self.pub_head_status.publish("HeadReaction Finished")
                            #rospy.loginfo(f"[{self.name}] ~180-degree roll rotation detected! Reaction time: {elapsed_time:.2f} seconds.")
                            self.reaction_active = False
                            self.initial_roll = None
                            rospy.sleep(1)
                            #rospy.signal_shutdown("Reaction time complete, exiting program!")
            else:
                self.initial_roll = None

            # rospy.loginfo(f"[{self.name}] Head detected at {head_position.round(3)}")
        else:
            rospy.logwarn_once(f"[{self.name}] Pose estimation failed.")


if __name__ == "__main__":
    rospy.init_node("multi_camera_aruco_head_tracker")

    # Start detector for hsrb camera only
    hsrb_cam = ArUcoHeadDetector(
        name="hsrb",
        image_topic="/hsrb/head_rgbd_sensor/rgb/image_raw",
        camera_info_topic="/hsrb/head_rgbd_sensor/rgb/camera_info",
        frame_id="head_rgbd_sensor_link"
    )

    rospy.spin()
