import torch
from torch.nn.modules.loss import _Loss
import torch.nn.functional as F

class BoundingBoxLoss(_Loss):
    def __init__(self, heatmap_weight=1.0, corner_weight=1.0):
        super().__init__()
        self.heatmap_weight = heatmap_weight
        self.corner_weight = corner_weight

    def forward(self, p_heatmap, p_corners, gt_heatmap, gt_corners):
        l2_heatmap_loss = F.mse_loss(torch.sigmoid(p_heatmap), gt_heatmap)
        where_support = (gt_heatmap > 0.0).repeat(1, 16, 1, 1)
        corner_loss = F.l1_loss(p_corners[where_support], gt_corners[where_support])
        return self.heatmap_weight * l2_heatmap_loss, self.corner_weight * corner_loss


