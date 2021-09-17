import cv2
import numpy as np
import open3d as o3d

class Camera:
    def __init__(self, K, D=np.zeros(4)):
        """
        K: 3 x 3 camera projection matrix.
        D: distortion parameters.
        """
        self.camera_matrix = K
        self.distortion = D

    def project(self, points, T_CW=np.eye(4)):
        """
        points: N x 3 3D points.
        T: optional transform matrix to convert points into camera coordinates.
        returns: N x 2 image coordinate points.
        """
        R, _ = cv2.Rodrigues(T_CW[:3, :3])
        out, _ = cv2.projectPoints(points, R, T_CW[:3, 3], self.camera_matrix, self.distortion)
        return out[:, 0, :]

def scale_intrinsics(o3d_intrinsics, new_width, new_height):
    old_height = o3d_intrinsics.height
    old_width = o3d_intrinsics.width
    if old_width == new_width and old_height == new_height:
        return o3d_intrinsics
    fx, fy = o3d_intrinsics.get_focal_length()
    cx, cy = o3d_intrinsics.get_principal_point()
    scale_x = new_width / old_width
    scale_y = new_height / old_height
    fx, fy = fx * scale_x, fy * scale_y
    cx, cy = cx * scale_x, fy * scale_y
    return o3d.camera.PinholeCameraIntrinsic(int(new_width), int(new_height), fx, fy, cx, cy)

