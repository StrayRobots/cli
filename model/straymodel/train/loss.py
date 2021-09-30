import torch
from torch.nn.modules.loss import _Loss
import torch.nn.functional as F

def spatial_softmax(predictions):
    """
    Convert predictions to heatmaps by normalizing over the 2d image.
    """
    N, H, W = predictions.shape
    return F.softmax(predictions.reshape(N, -1), dim=1).reshape(N, H, W)

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

    def forward(self, heatmap, depthmap, K, target):
        points3d = self._integrate_maps_unproject_points(heatmap, depthmap, K)
        return F.l1_loss(points3d, target)

class BoundingBoxLoss(_Loss):
    def __init__(self, size, center_weight=1.0, heatmap_weight=1.0, corner_weight=1.0):
        super().__init__()
        self.integral_loss = IntegralKeypointLoss(size)
        self.center_weight = center_weight
        self.heatmap_weight = heatmap_weight
        self.corner_weight = corner_weight

    def forward(self, p_heatmap, p_depth, p_corners, gt_heatmap, gt_corners, Ks, gt_points):
        center_loss = self.integral_loss(p_heatmap, p_depth, Ks, gt_points)
        l2_heatmap_loss = F.mse_loss(p_heatmap, gt_heatmap)
        corner_loss = F.l1_loss(p_corners, gt_corners)
        return (self.center_weight * center_loss +
                self.heatmap_weight * l2_heatmap_loss +
                self.corner_weight * corner_loss)


