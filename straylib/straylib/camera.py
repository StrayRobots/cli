import cv2
import numpy as np

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
