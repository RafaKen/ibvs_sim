#! /usr/bin/env python

## Simple ROS node that subcribes to pixel data in the fixed camera frame and
## transforms it to be expressed in virtual level camera frame
## JSW Nov 2017

import rospy
from sensor_msgs.msg import CameraInfo
from nav_msgs.msg import Odometry
from aruco_localization.msg import FloatList
import numpy as np
import cv2
import tf
import time


class LevelFrameMapper(object):

    def __init__(self):

        # load ROS params
        p_des = rospy.get_param('~p_des', [0., 0., 0., 0., 0., 0., 0., 0.])

        ## initialize other class variables
        
        # matrices to hold corner data
        self.corners = np.zeros((4,1,2))
        self.uv_bar_lf = np.zeros((4,2))  # pixel coords (u,v) of the corner points in the virtual level frame 

        self.f_row = np.zeros((1,4))

        # self.matrix = np.zeros((2,2), dtype=np.float32)

        # camera params
        self.K = np.zeros((3,3))
        self.d = np.zeros(5)
        self.fx = 0.0
        self.fy = 0.0
        self.cx = 0.0
        self.cy = 0.0
        self.f = 0.0

        # desired pixel coords 
        # [u1, v1, u2, v2, u3, v3, u4, v4].T  8x1
        self.p_des = np.array(p_des, dtype=np.float32).reshape(4,2)

        # copter attitude roll and pitch
        self.phi = 0.0
        self.theta = 0.0 

        # mounting angle offsets
        phi_m = 0.0    # roll relative to the body frame
        theta_m = 0.0  # pitch '...'
        psi_m = 0.0    # yaw '...'

        ## define fixed rotations
        sphi_m = np.sin(phi_m)
        cphi_m = np.cos(phi_m)
        stheta_m = np.sin(theta_m)
        ctheta_m = np.cos(theta_m)
        spsi_m = np.sin(psi_m )
        cpsi_m = np.cos(psi_m )

        # rotation from the virtual level frame to the vehicle 1 frame
        self.R_vlc_v1 = np.array([[0., -1., 0.],
                                  [1., 0., 0.],
                                  [0., 0., 1.]])

        # rotation from the body frame to the camera mount frame (same form as rotation from the vehicle to the body frame)
        self.R_b_m = np.array([[ctheta_m*cpsi_m, ctheta_m*spsi_m, -stheta_m],
                               [sphi_m*stheta_m*cpsi_m-cphi_m*spsi_m, sphi_m*stheta_m*spsi_m+cphi_m*cpsi_m, sphi_m*ctheta_m],
                               [cphi_m*stheta_m*cpsi_m+sphi_m*spsi_m, cphi_m*stheta_m*spsi_m-sphi_m*cpsi_m, cphi_m*ctheta_m]])

        # rotation from the mount frame to the camera frame
        self.R_m_c = np.array([[0., 1., 0.],
                               [-1., 0., 0.],
                               [0., 0., 1.]])


        # rotation from the vehicle 1 frame to the body frame (just initialize it--will update later)
        # self.R_v1_b = np.eye(3)

        # initialize rotation from camera frame to virtual level frame
        self.R_c_vlc = np.zeros((3,3))

        # initialize publishers
        self.uv_bar_pub = rospy.Publisher('/ibvs/uv_bar_lf', FloatList, queue_size=1)
        self.uv_bar_des_pub = rospy.Publisher('/ibvs/uv_bar_des', FloatList, queue_size=1)
        self.uv_bar_msg = FloatList()
        self.uv_bar_des_msg = FloatList()

        # initialize subscribers
        self.corner_pix_sub = rospy.Subscriber('/aruco/marker_corners', FloatList, self.corners_callback)
        self.attitude_sub = rospy.Subscriber('/quadcopter/estimate', Odometry, self.attitude_callback)
        self.camera_info_sub = rospy.Subscriber('/quadcopter/camera/camera_info', CameraInfo, self.camera_info_callback)


    def corners_callback(self, msg):

        # t = time.time()

        # populate corners matrix
        self.corners[0][0][0] = msg.data[0]
        self.corners[0][0][1] = msg.data[1]

        self.corners[1][0][0] = msg.data[2]
        self.corners[1][0][1] = msg.data[3]

        self.corners[2][0][0] = msg.data[4]
        self.corners[2][0][1] = msg.data[5]

        self.corners[3][0][0] = msg.data[6]
        self.corners[3][0][1] = msg.data[7]

        # undistort the corner locations
        corners_undist = cv2.undistortPoints(self.corners, self.K, self.d)

        # NOTE at this point we have normalized pixel coordinates
        # We want to de-normalize (multiply by focal length) but still want corner locations wrt image center

        # TODO vectorize this instead of corner by corner?? implemented below on 145 maybe it's not actually faster...

        corners_undist[0][0][0] = corners_undist[0][0][0]*self.fx
        corners_undist[0][0][1] = corners_undist[0][0][1]*self.fy

        corners_undist[1][0][0] = corners_undist[1][0][0]*self.fx
        corners_undist[1][0][1] = corners_undist[1][0][1]*self.fy

        corners_undist[2][0][0] = corners_undist[2][0][0]*self.fx
        corners_undist[2][0][1] = corners_undist[2][0][1]*self.fy

        corners_undist[3][0][0] = corners_undist[3][0][0]*self.fx
        corners_undist[3][0][1] = corners_undist[3][0][1]*self.fy

        # corners_undist = np.dot(corners_undist.reshape(4,2), self.matrix)

        corners_undist = corners_undist.reshape(4,2)

        # Transform the desired marker corner locations into the VLF 
        # desired_corners_vlf = self.transform_to_vlf(self.p_des)

        # Transform the actual marker corners into the VLF (input is 4x2 matrix of corners)
        actual_corners_vlf = self.transform_to_vlf(corners_undist)

        # fill out the FloatList messages
        # Desired corner loctions
        self.uv_bar_des_msg.header.frame_id = 'level-frame_corners'
        self.uv_bar_des_msg.header.stamp = msg.header.stamp # same as the incoming message
        self.uv_bar_des_msg.data = self.p_des.flatten().tolist()  # flatten and convert to list type

        # Actual corner locations
        self.uv_bar_msg.header.frame_id = 'level-frame_corners'
        self.uv_bar_msg.header.stamp = msg.header.stamp # same as the incoming message
        self.uv_bar_msg.data = actual_corners_vlf.flatten().tolist()  # flatten and convert to list type

        # publish
        self.uv_bar_des_pub.publish(self.uv_bar_des_msg)
        self.uv_bar_pub.publish(self.uv_bar_msg)

        # elapsed = time.time() - t
        # hz_approx = 1.0/elapsed
        # print(hz_approx)


    def transform_to_vlf(self, corners):

        # corners is a 4x2 matirx of undistorted center-relative corner pixel locations
        # store in a 3x4 matrix augmented with focal length (for convienience) and save for later
        uvf = np.concatenate((corners.T, self.f_row), axis=0)    # 3x4

        # setup rotations

        # pre-evaluate sines and cosines for rotation matrix
        sphi = np.sin(self.phi)
        cphi = np.cos(self.phi)
        stheta = np.sin(self.theta)
        ctheta = np.cos(self.theta)

        R_v1_v2 = np.array([[ctheta, 0., -stheta],
                            [0., 1., 0.],
                            [stheta, 0., ctheta]])

        R_v2_b = np.array([[1., 0., 0.],
                           [0., cphi, sphi],
                           [0., -sphi, cphi]])

        R_v1_b = np.dot(R_v2_b, R_v1_v2)

        # compute the whole rotation from camera frame to the virtual level frame
        self.R_c_vlc = self.R_m_c.dot(self.R_b_m.dot(R_v1_b.dot(self.R_vlc_v1))).T    # R_c_vlc = R_vlc_c.T

        # pass pixel locations through the rotation same way it's done in eq(14)
        
        # first, get the terms of eq(14)

        # this is how you'd do it one pixel (u, v) at a time:  
        # hom = np.dot(self.R_c_vlc, np.array([[corners_undist[0][0]],[corners_undist[0][1]],[self.f]]))  # this is a homography?? 3x1
        # x_term = hom[0][0]
        # y_term = hom[1][0]
        # denom = hom[2][0]

        # u_bar = self.f * (x_term/denom)
        # v_bar = self.f * (y_term/denom)

        # we'll do it all four corners at the same time:
        hom = np.dot(self.R_c_vlc, uvf) # 3x4
        
        # populate the matrix of (u,v) pixel coordinates in the virtual-level-frame
        self.uv_bar_lf[0][0] = self.f * (hom[0][0]/hom[2][0])   # u1
        self.uv_bar_lf[0][1] = self.f * (hom[1][0]/hom[2][0])   # v1

        self.uv_bar_lf[1][0] = self.f * (hom[0][1]/hom[2][1])   # u2
        self.uv_bar_lf[1][1] = self.f * (hom[1][1]/hom[2][1])   # v2

        self.uv_bar_lf[2][0] = self.f * (hom[0][2]/hom[2][2])   # u3
        self.uv_bar_lf[2][1] = self.f * (hom[1][2]/hom[2][2])   # v3

        self.uv_bar_lf[3][0] = self.f * (hom[0][3]/hom[2][3])   # u4
        self.uv_bar_lf[3][1] = self.f * (hom[1][3]/hom[2][3])   # v4

        # return a copy of 
        return self.uv_bar_lf.copy()




    def attitude_callback(self, msg):

        # get the quaternion orientation from the message
        quaternion = (
            msg.pose.pose.orientation.x,
            msg.pose.pose.orientation.y,
            msg.pose.pose.orientation.z,
            msg.pose.pose.orientation.w)

        # convert to euler angles 
        euler = tf.transformations.euler_from_quaternion(quaternion)

        # update class variables
        self.phi = euler[0]
        self.theta = euler[1]
        # print "roll: " + str(np.degrees(euler[0]))
        # print "pitch: " + str(np.degrees(euler[1]))


    def camera_info_callback(self, msg):

        # get the Camera Matrix K and distortion params d
        self.K = np.array(msg.K, dtype=np.float32).reshape((3,3))
        self.d = np.array(msg.D, dtype=np.float32)

        self.fx = self.K[0][0]
        self.fy = self.K[1][1]
        self.cx = self.K[0][2]
        self.cy = self.K[1][2]

        self.f = (self.fx + self.fy) / 2.0

        self.f_row[0][:] = self.f

        # self.matrix[0][0] = self.fx
        # self.matrix[1][1] = self.fy

        # just get this data once
        self.camera_info_sub.unregister()
        print("Level_frame_mapper: Got camera info!")




def main():
    # initialize a node
    rospy.init_node('level_frame_pixel_publisher')

    # create instance of LevelFrameMapper class
    mapper = LevelFrameMapper()

    # spin
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

    # OpenCV cleanup
    # cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
