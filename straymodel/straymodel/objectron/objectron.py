from straymodel.networks.straynet import StrayNet
import torch.optim as optim
import torch
import numpy as np
from straymodel.loss_functions.loss import BoundingBoxLoss
from straymodel.utils.train_utils import *
from straymodel.utils.visualization_utils import render_example
import pytorch_lightning as pl


class Objectron(pl.LightningModule):
    def __init__(self, heatmap_loss_coef, corner_loss_coef, lr):
        super().__init__()
        self.lr = lr
        self.model = StrayNet()
        self.heatmap_loss_coef = heatmap_loss_coef
        self.corner_loss_coef = corner_loss_coef
        self.loss_function = BoundingBoxLoss(heatmap_loss_coef, corner_loss_coef)
        self.save_hyperparameters()

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        images, heatmaps, corner_maps, intrinsics, _, sizes = batch
        p_heatmaps, _, p_corners = self(images)
        heatmap_loss, corner_loss = self.loss_function(p_heatmaps, p_corners, heatmaps, corner_maps)
        loss = heatmap_loss + corner_loss
        self.log('train_loss', loss)
        self.log('train_heatmap_loss', heatmap_loss)
        self.log('train_corner_loss', corner_loss)
        return loss

    def validation_step(self, batch, batch_idx):
        images, heatmaps, corner_maps, intrinsics, _, sizes = batch        
        p_heatmaps, _, p_corners = self(images)
        heatmap_loss, corner_loss = self.loss_function(p_heatmaps, p_corners, heatmaps, corner_maps)
        loss = heatmap_loss + corner_loss
        self.log('val_loss', loss)
        self.log('val_heatmap_loss', heatmap_loss)
        self.log('val_corner_loss', corner_loss)
        if batch_idx == 0:
            index = np.random.randint(0, p_heatmaps.shape[0])

            p_heatmap = torch.sigmoid(p_heatmaps[index])
            heatmap = heatmaps[index]

            image = images[index]

            corner_image = render_example(image.cpu().numpy(), heatmap.detach().cpu().numpy(),
                    corner_maps[index].detach().cpu().numpy(), intrinsics[index].detach().cpu().numpy(), sizes[index].detach().cpu().numpy())

            p_corner_image = render_example(image.cpu().numpy(), p_heatmap.detach().cpu().numpy(),
                    p_corners[index].detach().cpu().numpy(), intrinsics[index].detach().cpu().numpy(), sizes[index].detach().cpu().numpy())


            self.logger.experiment.add_image('p_heatmap', p_heatmap, self.global_step)
            self.logger.experiment.add_image('heatmap', heatmap, self.global_step)

            p_corner_image = np.transpose(p_corner_image, [2, 0, 1])
            corner_image = np.transpose(corner_image, [2, 0, 1])

            self.logger.experiment.add_image('p_corners', p_corner_image, self.global_step)
            self.logger.experiment.add_image('image', corner_image, self.global_step)
        
        return loss

    def configure_optimizers(self):
        return optim.Adam(self.model.parameters(), lr=self.lr)
