import torch
import torchvision.models as models
import torch.nn as nn


class StrayNet(torch.nn.Module):
    def __init__(self):
        super(StrayNet, self).__init__()
        self.backbone = models.mobilenet_v2()
        self.backbone.classifier[1] = nn.Linear(1280, 7)

    def forward(self, x):
        return self.backbone(x)

    def eval(self, train=False):
        self.backbone.eval()
        super(StrayNet, self).eval()

    def train(self, train=True):
        self.backbone.train()
        super(StrayNet, self).train()

    def to(self, device):
        print("tototo", device)
        self.backbone.to(device)
        super(StrayNet, self).to(device)