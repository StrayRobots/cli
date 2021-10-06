import torch
import torch.nn as nn
from torchvision.models import mobilenetv3
from torchvision.models._utils import IntermediateLayerGetter
from torchvision.models.mobilenetv2 import ConvBNActivation


class StrayNet(torch.nn.Module):
    def __init__(self, dropout=0.2):
        super(StrayNet, self).__init__()
        backbone = mobilenetv3.mobilenet_v3_large(pretrained=True, dilated=True).features

        # Gather the indices of blocks which are strided. These are the locations of C1, ..., Cn-1 blocks.
        # The first and last blocks are always included because they are the C0 (conv1) and Cn.
        stage_indices = [0] + [i for i, b in enumerate(backbone) if getattr(b, "_is_cn", False)] + [len(backbone) - 1]
        low_pos = stage_indices[-4]  # use C2 here which has output_stride = 8
        high_pos = stage_indices[-1]  # use C5 which has output_stride = 16
        low_channels = backbone[low_pos].out_channels
        high_channels = backbone[high_pos].out_channels

        self.backbone = IntermediateLayerGetter(backbone, return_layers={str(low_pos): 'low', str(high_pos): 'high'})
        self.upsample = nn.Sequential(
            nn.ConvTranspose2d(high_channels, low_channels, 2, 2),
            nn.ReLU(inplace=True)
        )
        self.intermediate = nn.Sequential(
            ConvBNActivation(low_channels * 2, 64, kernel_size=3, stride=1),
            ConvBNActivation(64, 64, kernel_size=3, stride=1)
        )
        self.dropout = nn.Dropout(p=dropout, inplace=True)
        self.heatmap_head = nn.Sequential(
            ConvBNActivation(64, 64, kernel_size=3, stride=1),
            nn.Conv2d(64, 1, kernel_size=1, stride=1, bias=True)
        )
        self.depthmap_head = nn.Sequential(
            ConvBNActivation(64, 64, kernel_size=3, stride=1),
            nn.Conv2d(64, 1, kernel_size=1, stride=1, bias=True)
        )
        self.corners_head = nn.Sequential(
            ConvBNActivation(64, 64, kernel_size=3, stride=1),
            nn.Conv2d(64, 16, kernel_size=1, stride=1, bias=True)
        )

        # Most values are zero so initialize with a large negative bias.
        self.heatmap_head[-1].bias.data = torch.log(torch.ones(1) * 0.01)
        # Guess 1m away for depth.
        self.depthmap_head[-1].bias.data[0] = 1.0

    def forward(self, x):
        features = self.backbone(x)
        features_high = self.upsample(features['high'])
        features = self.dropout(torch.cat([features['low'], features_high], dim=1))
        features = self.intermediate(features)
        return self.heatmap_head(features), self.depthmap_head(features), self.corners_head(features)

    def eval(self, train=False):
        for net in self.networks:
           net.eval()

    def train(self, train=True):
        for net in self.networks:
           net.train()

    @property
    def networks(self):
        return [
            self.backbone,
            self.upsample,
            self.intermediate,
            self.dropout,
            self.heatmap_head,
            self.depthmap_head,
            self.corners_head
        ]

    def to(self, device):
       for net in self.networks:
           net.to(device)
