from straylib import camera
from straymodel.data.dataset import Stray3DBoundingBoxDetectionDataset
import click
from torch.utils.data import DataLoader
from straymodel.models.straynet import StrayNet
import torch.optim as optim
import torch.nn as nn
import torch
from straymodel.train.loss import BoundingBoxLoss
import os
import numpy as np
import cv2
from straylib.scene import cube_indices


def extract_corners_from_maps(corner_map, scale):
    corners = []
    for i in range(8):
        x_map = abs(corner_map.cpu().numpy()[i*2])
        y_map = abs(corner_map.cpu().numpy()[i*2 +1])
        x_min = np.unravel_index(np.argmin(x_map, axis=None), x_map.shape)
        y_min = np.unravel_index(np.argmin(y_map, axis=None), y_map.shape)
        corners.append((int(scale*x_min[1]), int(scale*y_min[0])))
    return corners

def save_example_images(images, center_maps, corner_maps, save_folder):
    for i, (image, center_map, corner_map) in enumerate(zip(images, center_maps, corner_maps)):
        _, cm_height, _ = center_map.size()
        _, height, width = image.size()
        corners = extract_corners_from_maps(corner_map, height/cm_height)
        cv_image = np.moveaxis(image.cpu().numpy()*255, 0, -1).astype(np.uint8)
        cv_center_map = np.moveaxis(center_map.cpu().numpy()*255, 0, -1).astype(np.uint8)
        heatmap_img = cv2.applyColorMap(cv_center_map, cv2.COLORMAP_JET)
        heatmap_img = cv2.resize(heatmap_img, (width, height))
        heatmap_img = cv2.addWeighted(cv_image, 0.3, heatmap_img, 0.7, 0)
        for corner1, vertex1 in zip(corners, cube_indices):
            cv2.circle(heatmap_img, corner1, 5, (0,255,0), -1)
            for corner2, vertex2 in zip(corners, cube_indices):
                if np.linalg.norm(vertex1-vertex2) == 1:
                    heatmap_img = cv2.line(heatmap_img, corner1, corner2, (0, 255, 0), 3)

        cv2.imwrite(os.path.join(save_folder, f"heat_{i}.png"), heatmap_img)



torch.cuda.empty_cache()

@click.command()
@click.argument('scenes', nargs=-1)
@click.option('--batch-size', type=int, default=2)
@click.option('--debug-save-folder', default="./") #TODO: not to be included in "final" version
@click.option('--num-workers', type=int, default=1)
@click.option('--num-epochs', type=int, default=1)
@click.option('--shuffle', is_flag=True)
def train(scenes, batch_size, debug_save_folder, num_workers, num_epochs, shuffle):
    dataset = Stray3DBoundingBoxDetectionDataset(scenes, out_size=(80, 60))
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)
    model = StrayNet()

    #TODO: set device globally
    if torch.cuda.is_available():
        device = "cuda:0"
    else:
        device = "cpu"
    model.to(device)

    loss_function = BoundingBoxLoss((80, 60))
    optimizer = optim.Adam(model.parameters())

    model.train()

    os.makedirs(os.path.join(debug_save_folder, "examples"), exist_ok=True)

    for epoch in range(num_epochs):
        epoch_dir = os.path.join(debug_save_folder, f"epoch_{epoch}")
        os.makedirs(epoch_dir, exist_ok=True)
        epoch_corner_loss = 0.0
        epoch_center_loss = 0.0
        epoch_heatmap_loss = 0.0
        for i, batch in enumerate(dataloader):
            print("Batch", i, "/", len(dataloader), end='\r')
            images, center_maps, corner_maps, cameras, centers = batch
            images = images.to(device)
            center_maps = center_maps.to(device)
            corner_maps = corner_maps.to(device)
            cameras = cameras.to(device)
            centers = centers.to(device)

            optimizer.zero_grad()
            p_heatmaps, p_depthmaps, p_corners = model(images)
            
            center_loss, heatmap_loss, corner_loss = loss_function(p_heatmaps, p_depthmaps, p_corners, center_maps, corner_maps, cameras, centers)
            loss = center_loss + heatmap_loss + corner_loss

            loss.backward()
            optimizer.step()

            epoch_corner_loss += corner_loss.item()
            epoch_center_loss += center_loss.item()
            epoch_heatmap_loss += heatmap_loss.item()
            
            #TODO: not to be included in "final" version, currently saves examples of last batch from epoch
            if epoch == 0 and i == 0:
                save_example_images(images, center_maps, corner_maps, os.path.join(debug_save_folder, "examples"))
            
        #TODO: not to be included in "final" version, currently saves examples of last batch from epoch
        save_example_images(images.detach(), p_heatmaps.detach(), p_corners.detach(), epoch_dir)

        print(f"Epoch {epoch} corner loss: {epoch_corner_loss} center loss: {epoch_center_loss} heatmap loss: {epoch_heatmap_loss}")


if __name__ == "__main__":
    train()