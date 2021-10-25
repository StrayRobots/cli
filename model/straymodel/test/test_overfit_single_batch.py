import pytest
import torch
import random
import os
import numpy as np
import torch.optim as optim
import torch.nn as nn
from torch.nn import functional as F
import pathlib
from straymodel.data.dataset import Stray3DBoundingBoxDetectionDataset
from torch.utils.data import DataLoader
from straymodel.models.straynet import StrayNet
from straymodel.train.loss import BoundingBoxLoss

def seed(seed=123):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


@pytest.mark.slow
def test_overfit_single_batch():
    if torch.cuda.is_available():
        device = 'cuda:0'
    else:
        device = 'cpu'
    seed()
    parent_path = pathlib.Path(__file__).parent.parent.absolute()
    test_scene_path = os.path.join(parent_path, "fixtures", "scene1")
    dataset = Stray3DBoundingBoxDetectionDataset([test_scene_path], image_size=(640, 480), out_size=(80, 60))
    dataloader = DataLoader(dataset, batch_size=2, shuffle=False, num_workers=0)
    model = StrayNet(dropout=0.0)
    model.to(device)

    loss = BoundingBoxLoss((80, 60), device=device)
    optimizer = optim.SGD(model.parameters(), lr=1.0)
    schedule = optim.lr_scheduler.StepLR(optimizer, gamma=0.1, step_size=250)

    model.train()
    single_batch = next(iter(dataloader))
    images, gt_heatmap, gt_corners, Ks, gt_points, size = [t.to(device) for t in single_batch]

    for _ in range(1000):
        optimizer.zero_grad()
        p_heatmaps, p_depth, p_corners = model(images)
        center_loss, heatmap_loss, corner_loss = loss(p_heatmaps, p_depth, p_corners, gt_heatmap, gt_corners, Ks, gt_points)
        loss_value = center_loss + heatmap_loss + corner_loss
        loss_value.backward()
        optimizer.step()
        schedule.step()

    model.eval()
    p_heatmaps, p_depth, p_corners = model(images)
    p_depth = F.relu(p_depth)
    loss_values = loss(p_heatmaps, p_depth, p_corners, gt_heatmap, gt_corners, Ks, gt_points)
    loss_value = sum(loss_values)

    assert loss_value.cpu().item() < 0.25

