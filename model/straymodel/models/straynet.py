import torch
import torchvision.models as models
import torch.nn as nn


class StrayNet(torch.nn.Module):
    def __init__(self):
        super(StrayNet, self).__init__()
        self.backbone = models.mobilenet_v3_large()
        del self.backbone.classifier
        self.head = nn.Linear(960, 7) #Change to actual heads

    def forward(self, x):
        x = self.backbone(x)
        x = self.head(x)
        return x

    def eval(self, train=False):
        self.backbone.eval()
        super(StrayNet, self).eval()

    def train(self, train=True):
        self.backbone.train()
        super(StrayNet, self).train()

    def to(self, device):
        self.backbone.to(device)
        super(StrayNet, self).to(device)