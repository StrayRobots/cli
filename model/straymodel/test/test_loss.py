import unittest
import torch
import cv2
import numpy as np
from torch import optim
from straymodel.train.loss import *
from straymodel.utils.heatmap_utils import paint_heatmap
import torch.nn.functional as F
from scipy.spatial.transform import Rotation

WIDTH = 128
HEIGHT = 128
K = np.array([[128., 0.0, 64.56],
        [0.0, 128., 64.6],
        [0.0, 0.0, 1.0]])
D = np.zeros(4)

class LossTestCase(unittest.TestCase):
    def test_2d_to_3d(self):
        keypoint = np.array([0., 0., 2.]) # Front and center, two meters away.
        heatmap = np.zeros((1, 1, WIDTH, HEIGHT))
        point2d, _ = cv2.projectPoints(keypoint[None, None, :], np.zeros(3), np.zeros(3), K, D)
        point2d = point2d.ravel()[None]
        paint_heatmap(heatmap[0, 0], point2d, 10.0)
        self.assertEqual(heatmap.min(), 0.0)

        heatmap = torch.tensor(heatmap)
        depth_map = torch.ones((1, 1, HEIGHT, WIDTH)) * 2.0
        loss = IntegralKeypointLoss((HEIGHT, WIDTH))
        heatmap /= heatmap.sum()
        points3d = loss._integrate_maps_unproject_points(heatmap, depth_map, torch.tensor(K)).detach().numpy()
        np.testing.assert_allclose(points3d[0], keypoint, atol=1e-2)

    def test_optimize_for_value(self):
        keypoint = np.random.uniform([-0.1, -0.1, 0.9], [0.1, 0.1, 1.1])
        point2d, _ = cv2.projectPoints(keypoint[None, None, :], np.zeros(3), np.zeros(3), K, D)
        point2d = point2d.ravel()[None]
        keypoint = torch.tensor(keypoint)[None]

        initial_guess = torch.ones(1, 1, HEIGHT, WIDTH).to(torch.float64)
        x_heatmap = initial_guess.requires_grad_(True)
        x_depth = torch.ones(1, 1, HEIGHT, WIDTH, dtype=torch.float64).requires_grad_(True)
        optimizer = optim.SGD([x_depth, x_heatmap], lr=1000.0, momentum=0.9)
        schedule = optim.lr_scheduler.StepLR(optimizer, gamma=0.1, step_size=50)

        K_tensor = torch.tensor(K)
        loss = IntegralKeypointLoss((HEIGHT, WIDTH))
        for _ in range(200):
            optimizer.zero_grad()
            value = loss(spatial_softmax(x_heatmap), x_depth, K_tensor, keypoint)
            value.backward()
            optimizer.step()
            schedule.step()

        points3d = loss._integrate_maps_unproject_points(spatial_softmax(x_heatmap), x_depth, torch.tensor(K)).detach().numpy()
        np.testing.assert_allclose(points3d[0], keypoint[0], rtol=1e-2, atol=1e-2)

    def test_optimize_batch(self):
        N = 2
        keypoints = np.zeros((N, 3))
        for i in range(N):
            keypoints[i] = np.random.uniform([-0.1, -0.1, 0.9], [0.1, 0.1, 1.1], size=3)
            point2d, _ = cv2.projectPoints(keypoints[i][None, None, :], np.zeros(3), np.zeros(3), K, D)
            point2d = point2d.ravel()[None]

        keypoints = torch.tensor(keypoints)

        x_heatmap = torch.ones(N, 1, HEIGHT, WIDTH, dtype=torch.float64).requires_grad_(True)
        x_depth = torch.ones(N, 1, HEIGHT, WIDTH, dtype=torch.float64).requires_grad_(True)
        optimizer = optim.SGD([x_depth, x_heatmap], lr=1000.0, momentum=0.9)
        schedule = optim.lr_scheduler.StepLR(optimizer, gamma=0.1, step_size=50)
        K_tensor = torch.tensor(K)
        loss = IntegralKeypointLoss((HEIGHT, WIDTH))
        for _ in range(250):
            optimizer.zero_grad()
            value = loss(spatial_softmax(x_heatmap), x_depth, K_tensor, keypoints)
            value.backward()
            optimizer.step()
            schedule.step()

        points3d = loss._integrate_maps_unproject_points(spatial_softmax(x_heatmap), x_depth, torch.tensor(K)).detach().numpy()
        np.testing.assert_allclose(points3d, keypoints.numpy(), rtol=1e-2, atol=1e-2)

    def test_full_loss(self):
        center = np.random.uniform(np.ones(3) * -0.1, np.ones(3) * 0.1) + np.array([0., 0., 1.])
        bbox = np.array([-1., -1., -1.,
            -1., -1.,  1.,
            -1.,  1., -1.,
            -1.,  1.,  1.,
             1., -1., -1.,
             1., -1.,  1.,
             1.,  1., -1.,
             1.,  1.,  1.]).reshape((8, 3)) * 0.1
        R = Rotation.random()
        bbox = R.apply(bbox)
        bbox += center
        points2d, _ = cv2.projectPoints(bbox[:, None, :], np.zeros(3), np.zeros(3), K, D)
        points2d = points2d.reshape(8, 2)
        center2d, _ = cv2.projectPoints(center[None, None, :], np.zeros(3), np.zeros(3), K, D)
        center2d = center2d.ravel()
        heatmap = np.zeros((1, 1, HEIGHT, WIDTH))
        paint_heatmap(heatmap[0, 0], center2d[None], 1.0)
        heatmap /= heatmap.sum()
        corners = np.zeros((1, 16, HEIGHT, WIDTH))
        for i, point in enumerate(points2d):
            vector = center2d - point
            vector_field = vector[:, None, None].repeat(HEIGHT, axis=1).repeat(WIDTH, axis=2)
            index = i*2
            corners[:, index:index+2] = vector_field
        loss = BoundingBoxLoss((HEIGHT, WIDTH))
        depth = np.ones((1, 1, HEIGHT, WIDTH)) * center[2]
        heatmap, depth, corners, center = torch.tensor(heatmap), torch.tensor(depth), torch.tensor(corners), torch.tensor(center)
        K_tensor = torch.tensor(K)
        heatmap /= heatmap.max()
        center_loss, heatmap_loss, corner_loss = loss(torch.log(heatmap + 1e-16), depth, corners, heatmap, corners, K_tensor, center[None])
        self.assertAlmostEqual(center_loss.item(), 0.0, 2)
        self.assertAlmostEqual(heatmap_loss.item(), 0.0, 2)
        self.assertAlmostEqual(corner_loss.item(), 0.0, 2)

        p_heatmap = torch.log(heatmap + 1e-6).requires_grad_(True)
        p_depth = depth.clone().requires_grad_(True)
        p_corners = corners.clone().requires_grad_(True)
        optimizer = optim.SGD([p_heatmap, p_depth, p_corners], lr=1e-1)
        schedule = optim.lr_scheduler.StepLR(optimizer, gamma=0.1, step_size=500)
        for _ in range(2000):
            optimizer.zero_grad()
            values = loss(p_heatmap, p_depth, p_corners, heatmap, corners, K_tensor, center[None])
            value = sum(values)
            value.backward()
            optimizer.step()
            schedule.step()
        self.assertLess(value.item(), 1e-2)
        #TODO: figure out why the heatmaps don't match exactly.
        self.assertEqual(spatial_softmax(p_heatmap).argmax().item(), heatmap.argmax().item())
        np.testing.assert_allclose(p_corners.detach().numpy(), corners.numpy())
        np.testing.assert_allclose(p_depth.detach().numpy(), depth.numpy(), rtol=0.1, atol=1e-3)


if __name__ == "__main__":
    unittest.main()
