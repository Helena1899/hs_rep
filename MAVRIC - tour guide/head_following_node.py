#!/usr/bin/env python3
import rospy
import cv2
import numpy as np
import torch
from sensor_msgs.msg import Image, CameraInfo, JointState, CompressedImage
from geometry_msgs.msg import TransformStamped
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from cv_bridge import CvBridge
import tf2_ros
from tf.transformations import quaternion_from_euler
from ultralytics import YOLO

class HiVisDetectorNode:
    def __init__(self):

        # initialize hi-vis detector node
        rospy.init_node('hivis_detector_node')

        # download model if necessary
        self.model = YOLO("/home/helenasi/Downloads/HiVisModel.pt")
        self.model.fuse()

        # use cv face detection model
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.bridge = CvBridge()
        self.tf_broadcaster = tf2_ros.TransformBroadcaster()

        # shows face and human detections in topic in rqt_image_view
        self.annotated_image_pub = rospy.Publisher("/pose_annotated_image", Image, queue_size=1)
        self.head_pub = rospy.Publisher("/hsrb/head_trajectory_controller/command", JointTrajectory, queue_size=1)

        # sets camera parameteers
        self.fx = self.fy = self.cx = self.cy = None
        self.image_width = 640
        self.image_height = 480
        self.depth_image = None

        self.head_pan = 0.0
        self.head_tilt = 0.0
        self.smoothed_cx = None
        self.smoothed_cy = None
        self.smoothing_alpha = 0.3
        self.move_threshold = 10
        self.last_head_update = rospy.Time.now()
        self.head_update_interval = rospy.Duration(0.5)

        # sets fine-tuning parameters for PID to control head movements
        self.Kp_pan = 0.5 # 0.5
        self.Ki_pan = 0.0
        self.Kd_pan = 0.5 # 0.5
        self.pan_integral = 0.0
        self.last_pan_error = 0.0

        self.Kp_tilt = 0.5
        self.Ki_tilt = 0.0
        self.Kd_tilt = 0.5
        self.tilt_integral = 0.0
        self.last_tilt_error = 0.0

        self.last_pid_time = rospy.Time.now()

        # get data from the rgbd sensor topics on robot
        self.image_sub = rospy.Subscriber("/hsrb/head_rgbd_sensor/rgb/image_rect_color", Image, self.image_callback)
        self.depth_sub = rospy.Subscriber("/hsrb/head_rgbd_sensor/depth_registered/image_rect_raw", Image, self.depth_callback)
        self.camera_info_sub = rospy.Subscriber("/hsrb/head_rgbd_sensor/depth_registered/camera_info", CameraInfo, self.cam_info_callback)
        self.joint_state_sub = rospy.Subscriber("/hsrb/joint_states", JointState, self.joint_state_callback)


        self.sub_experiment_status = rospy.Subscriber("/hsrb/joint_states", JointState, self.joint_state_callback) ## Guide Mode: 4, Explanation Mode: 3


    def cam_info_callback(self, msg):
        self.fx = msg.K[0]
        self.fy = msg.K[4]
        self.cx = msg.K[2]
        self.cy = msg.K[5]
        self.image_width = msg.width
        self.image_height = msg.height

    def depth_callback(self, msg):
        self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')

    def joint_state_callback(self, msg):
        for i, name in enumerate(msg.name):
            if name == "head_pan_joint":
                self.head_pan = msg.position[i]
            elif name == "head_tilt_joint":
                self.head_tilt = msg.position[i]

    # move head to follow human function; do you want to test it now? i am free at 1pm. ios ktahat ok? okay. it is up to you. can I test some codes now?yes of course
    def move_head_to_target(self, cx, cy):
        now = rospy.Time.now()
        if now - self.last_head_update < self.head_update_interval:
            return

        if self.smoothed_cx is None:
            self.smoothed_cx = cx
            self.smoothed_cy = cy

        alpha = self.smoothing_alpha
        self.smoothed_cx = alpha * cx + (1 - alpha) * self.smoothed_cx
        self.smoothed_cy = alpha * cy + (1 - alpha) * self.smoothed_cy

        if abs(self.smoothed_cx - self.cx) < self.move_threshold and abs(self.smoothed_cy - self.cy) < self.move_threshold:
            return

        self.last_head_update = now

        current_time = rospy.Time.now()
        dt = (current_time - self.last_pid_time).to_sec()
        if dt == 0:
            return
        self.last_pid_time = current_time

        error_x = self.smoothed_cx - self.cx
        error_y = self.smoothed_cy - self.cy

        fov_x_rad = np.deg2rad(60)
        fov_y_rad = np.deg2rad(45)
        angle_error_x = (error_x / self.image_width) * fov_x_rad
        angle_error_y = (error_y / self.image_height) * fov_y_rad

        self.pan_integral += angle_error_x * dt
        pan_derivative = (angle_error_x - self.last_pan_error) / dt
        pan_correction = -(self.Kp_pan * angle_error_x + self.Ki_pan * self.pan_integral + self.Kd_pan * pan_derivative)
        self.last_pan_error = angle_error_x

        self.tilt_integral += angle_error_y * dt
        tilt_derivative = (angle_error_y - self.last_tilt_error) / dt
        tilt_correction = -(self.Kp_tilt * angle_error_y + self.Ki_tilt * self.tilt_integral + self.Kd_tilt * tilt_derivative)
        self.last_tilt_error = angle_error_y

        max_pan = 2.5
        max_tilt = 1.5
        new_pan = np.clip(self.head_pan + pan_correction, -max_pan, max_pan)
        new_tilt = np.clip(self.head_tilt + tilt_correction, -max_tilt, max_tilt)

        traj = JointTrajectory()
        traj.joint_names = ["head_pan_joint", "head_tilt_joint"]
        point = JointTrajectoryPoint()
        point.positions = [new_pan, new_tilt]
        point.velocities = [0, 0]
        point.time_from_start = rospy.Duration(0.5)
        traj.points = [point]
        self.head_pub.publish(traj)

    def image_callback(self, msg):
        if self.depth_image is None or None in (self.fx, self.fy, self.cx, self.cy):
            return
        
        rgb_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        annotated_img = rgb_image.copy()
        target_found = False
        target_cx = target_cy = None

        ### HI-VIS Detection ###
        results = self.model(rgb_image)[0]

        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = self.model.names[cls_id]
            if label == "hi-vis":
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                target_cx, target_cy = cx, cy
                target_found = True
                try:
                    depth = self.depth_image[cy, cx] / 1000.0
                except IndexError:
                    continue
                if depth <= 0 or np.isnan(depth):
                    continue
                X = (cx - self.cx) * depth / self.fx
                Y = (cy - self.cy) * depth / self.fy
                Z = depth

                # calculate angle from camera and transform to quaternion
                angle_x = np.arctan2(X, Z)
                angle_y = np.arctan2(Y, Z)
                quat = quaternion_from_euler(-angle_y, angle_x, 0)

                # publish tf transform on rviz
                t = TransformStamped()
                t.header.stamp = msg.header.stamp
                t.header.frame_id = "head_rgbd_sensor_link"
                t.child_frame_id = "human_body"
                t.transform.translation.x = X
                t.transform.translation.y = Y
                t.transform.translation.z = Z
                t.transform.rotation.x = quat[0]
                t.transform.rotation.y = quat[1]
                t.transform.rotation.z = quat[2]
                t.transform.rotation.w = quat[3]
                self.tf_broadcaster.sendTransform(t)

                cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(annotated_img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


        ### FACE DETECTION ###
        face_found = False
        fcx = fcy = None

        gray = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        
        # get a point towards the eyes of the face
        if len(faces) > 0:
            fx1, fy1, fw, fh = faces[0]
            fx2 = fx1 + fw
            fy2 = fy1 + fh
            fcx = fx1 + fw // 2
            fcy = fy1 + fh // 4
            face_found = True
            try:
                face_depth = self.depth_image[fcy, fcx] / 1000.0
            except IndexError:
                face_found = False
            if face_found and (face_depth <= 0 or np.isnan(face_depth)):
                face_found = False

            if face_found:
                Xf = (fcx - self.cx) * face_depth / self.fx
                Yf = (fcy - self.cy) * face_depth / self.fy
                Zf = face_depth

                # get angles from camera and transform to quaternion
                angle_xf = np.arctan2(Xf, Zf)
                angle_yf = np.arctan2(Yf, Zf)
                quat_f = quaternion_from_euler(-angle_yf, angle_xf, 0)

                '''
                # publish tf
                t = TransformStamped()
                t.header.stamp = msg.header.stamp
                t.header.frame_id = "head_rgbd_sensor_link"
                t.child_frame_id = "human_face"
                t.transform.translation.x = Xf
                t.transform.translation.y = Yf
                t.transform.translation.z = Zf
                t.transform.rotation.x = quat_f[0]
                t.transform.rotation.y = quat_f[1]
                t.transform.rotation.z = quat_f[2]
                t.transform.rotation.w = quat_f[3]
                self.tf_broadcaster.sendTransform(t)
                '''
                
                cv2.rectangle(annotated_img, (fx1, fy1), (fx2, fy2), (255, 0, 0), 2)
                cv2.putText(annotated_img, "face", (fx1, fy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        ros_img = self.bridge.cv2_to_imgmsg(annotated_img, "bgr8")
        ros_img.header.stamp = msg.header.stamp
        ros_img.header.frame_id = "head_rgbd_sensor_link"
        self.annotated_image_pub.publish(ros_img)

        # if both hi-vis and face are detected, focus point should be the average distance between detections
        if target_found and face_found:
            mid_cx = (target_cx + fcx) // 2
            mid_cy = (target_cy + fcy) // 2
            self.move_head_to_target(mid_cx, mid_cy)
        
        # if hi-vis is detected, focus point should be on the hi-vis center coordinates
        elif target_found:
            self.move_head_to_target(target_cx, target_cy - 100)

        # if face is detected, focus point should be on the face center coordinates
        elif face_found:
            pass            
            #self.move_head_to_target(fcx, fcy)

        # if none are detected, look straight
        else:
            pass
            #center_x = self.image_width // 2
            #center_y = self.image_height // 2
            #self.move_head_to_target(center_x, center_y)


if __name__ == '__main__':
    try:
        HiVisDetectorNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass