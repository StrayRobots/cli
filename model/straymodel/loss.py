import torch
from torch.nn.modules.loss import _Loss
import torch.nn.functional as F


class IntegralKeypointLoss(_Loss):
    def __init__(self, size):
        super().__init__()
        self.indices = torch.zeros((*size, 2), dtype=torch.float)
        for i in range(size[0]):
            for j in range(size[1]):
                self.indices[i, j, :] = torch.tensor((j, i), dtype=torch.float)
        self.indices = self.indices[None]

    def _integrate_maps_unproject_points(self, heatmap, depthmap, K):
        heatmap_double = heatmap[:, :, :, None].repeat(1, 1, 1, 2)
        points2d = (self.indices * heatmap_double).sum(dim=[1, 2]) / heatmap.sum(dim=[1,2])
        depth = depthmap * heatmap
        depth = depth.sum(dim=[1, 2])

        fx = K[..., 0, 0]
        fy = K[..., 1, 1]
        cx = K[..., 0, 2]
        cy = K[..., 1, 2]

        x = (points2d[..., 0] - cx) / fx
        y = (points2d[..., 1] - cy) / fy
        xyz = torch.stack([x, y, torch.ones_like(x)], dim=-1)
        return xyz * depth[:, None]

    def _heatmap(self, x):
        # x: N x H x W
        N, H, W = x.shape
        return F.softmax(x.reshape(N, -1), dim=1).reshape(N, H, W)

    def forward(self, prediction, depthmap, K, target):
        heatmap = self._heatmap(prediction)
        points3d = self._integrate_maps_unproject_points(heatmap, depthmap, K)
        return F.l1_loss(points3d, target)

