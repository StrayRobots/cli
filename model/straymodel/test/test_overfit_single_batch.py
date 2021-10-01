import pytest
import torch
import random
import os
import numpy as np
from straymodel.data.dataset import Stray3DSceneDataset
from torch.utils.data import DataLoader
from straymodel.models.straynet import StrayNet
import torch.optim as optim
import torch.nn as nn
import torch
import numpy as np
import pathlib

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
    seed()
    parent_path = pathlib.Path(__file__).parent.parent.absolute()
    test_scene_path = os.path.join(parent_path, "fixtures", "scene1")
    dataset = Stray3DSceneDataset([test_scene_path], 100, 100)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=False, num_workers=1)
    model = StrayNet()

    loss_functions = [nn.MSELoss()]
    optimizer = optim.Adam(model.parameters())

    model.train()
    single_batch = next(iter(dataloader))
    images, poses = single_batch
    for _ in range(1000):
        optimizer.zero_grad()
        outputs = model(images)
        loss = sum([loss_func(outputs, poses) for loss_func in loss_functions])
        loss.backward()
        optimizer.step()
    
    model.eval()
    eval_outputs = model(images)
    eval_loss = sum([loss_func(eval_outputs, poses) for loss_func in loss_functions])

    assert np.isclose(eval_loss.item(), 0.0033829514868557453) #TODO: fails, this result was with mobilenet_v3


