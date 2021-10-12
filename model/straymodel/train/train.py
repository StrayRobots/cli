from straymodel.data.dataset import Stray3DBoundingBoxDetectionDataset
import click
from torch.utils.data import DataLoader
from straymodel.models.straynet import StrayNet
import torch.optim as optim
import torch
from straymodel.train.loss import BoundingBoxLoss, spatial_softmax
from straymodel.utils.visualization_utils import save_example, save_dataset_snapshot
import os
from torch.utils.data import random_split

def eval_loop(test_loader, device, model, loss_function, epoch, progress_save_folder, save_examples=10, save_model_every_epoch=10):
    test_epoch_corner_loss = 0.0
    test_epoch_center_loss = 0.0
    test_epoch_heatmap_loss = 0.0
    epoch_dir = os.path.join(progress_save_folder, f"epoch_{epoch}")
    os.makedirs(epoch_dir, exist_ok=True)
    
    model.eval()
    for i, batch in enumerate(test_loader):
        print("Test Batch", i, "/", len(test_loader), end='\r')
        images, center_maps, heatmaps, cameras, centers, sizes = [item.to(device) for item in batch]

        p_heatmaps, p_depthmaps, p_corners = model(images)
    
        center_loss, heatmap_loss, corner_loss = loss_function(p_heatmaps, p_depthmaps, p_corners, center_maps, heatmaps, cameras, centers)
        test_epoch_corner_loss += corner_loss.item()
        test_epoch_center_loss += center_loss.item()
        test_epoch_heatmap_loss += heatmap_loss.item()

        if i < (save_examples-1):
            save_example(images[0].cpu().numpy(), spatial_softmax(p_heatmaps)[0].detach().cpu().numpy(), p_corners[0].detach().cpu().numpy(), cameras[0].cpu().numpy(), sizes[0].cpu().numpy(), epoch_dir, i)

    if epoch % save_model_every_epoch == 0:
        script_model = torch.jit.script(model)
        torch.jit.save(script_model, os.path.join(epoch_dir, "model.pt"))

    print(f"Epoch {epoch} test corner loss: {test_epoch_corner_loss} center loss: {test_epoch_center_loss} heatmap loss: {test_epoch_heatmap_loss}")
    

def train_loop(train_loader, device, optimizer, model, loss_function, epoch):
    epoch_corner_loss = 0.0
    epoch_center_loss = 0.0
    epoch_heatmap_loss = 0.0
    model.train()
    for i, batch in enumerate(train_loader):
        print("Batch", i, "/", len(train_loader), end='\r')
        images, heatmaps, corner_maps, cameras, centers, _ = [item.to(device) for item in batch]

        optimizer.zero_grad()
        p_heatmaps, p_depthmaps, p_corners = model(images)
        
        center_loss, heatmap_loss, corner_loss = loss_function(p_heatmaps, p_depthmaps, p_corners, heatmaps, corner_maps, cameras, centers)
        loss = center_loss + heatmap_loss + corner_loss

        loss.backward()
        optimizer.step()

        epoch_corner_loss += corner_loss.item()
        epoch_center_loss += center_loss.item()
        epoch_heatmap_loss += heatmap_loss.item()
        

    print(f"Epoch {epoch} train corner loss: {epoch_corner_loss} center loss: {epoch_center_loss} heatmap loss: {epoch_heatmap_loss}")

@click.command()
@click.argument('scenes', nargs=-1)
@click.option('--batch-size', type=int, default=2)
@click.option('--split-size', type=float, default=0.8)
@click.option('--progress-save-folder', default="./")
@click.option('--num-workers', type=int, default=1)
@click.option('--num-epochs', type=int, default=1)
@click.option('--heatmap-loss-coef', type=int, default=1)
@click.option('--center-loss-coef', type=int, default=1)
@click.option('--corner-loss-coef', type=int, default=1)
@click.option('--shuffle', is_flag=True)
def train(scenes, batch_size, split_size, progress_save_folder, num_workers, num_epochs, heatmap_loss_coef, center_loss_coef, corner_loss_coef, shuffle):
    dataset = Stray3DBoundingBoxDetectionDataset(scenes, out_size=(80, 60))

    train_size = int(split_size * len(dataset))
    test_size = len(dataset) - train_size

    train_dataset, test_dataset = random_split(dataset, [train_size, test_size])
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)
    test_loader = DataLoader(test_dataset, batch_size=1, shuffle=shuffle, num_workers=num_workers)
    os.makedirs(progress_save_folder, exist_ok=True)
    save_dataset_snapshot(train_loader, progress_save_folder)

    model = StrayNet()

    #TODO: set device globally
    if torch.cuda.is_available():
        device = "cuda:0"
    else:
        device = "cpu"
    model.to(device)

    loss_function = BoundingBoxLoss((80, 60), center_loss_coef, heatmap_loss_coef, corner_loss_coef)
    optimizer = optim.Adam(model.parameters())

    for epoch in range(num_epochs):
        train_loop(train_loader, device, optimizer, model, loss_function, epoch)
        eval_loop(test_loader, device, model, loss_function, epoch, progress_save_folder)

if __name__ == "__main__":
    train()