from data.dataset import Stray3DSceneDataset
import click
from torch.utils.data import DataLoader
from models.straynet import StrayNet
import torch.optim as optim
import torch.nn as nn
import torch

@click.command()
@click.argument('scenes', nargs=-1)
@click.option('--batch-size', type=int, default=2)
@click.option('--num-workers', type=int, default=1)
@click.option('--num-epochs', type=int, default=1)
@click.option('--shuffle', is_flag=True)
def train(scenes, batch_size, num_workers, num_epochs, shuffle):
    dataset = Stray3DSceneDataset(scenes)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)
    model = StrayNet()

    if torch.cuda.is_available():
        device = "cuda:0"
    else:
        device = "cpu"
    model.to(device)

    loss_functions = [nn.MSELoss()]
    optimizer = optim.Adam(model.parameters())

    model.train()
    for epoch in range(num_epochs):
        epoch_loss = 0.0
        for batch in dataloader:
            images = batch["image"]
            images = images.to(device)
            poses = batch["annotations"][0]["pose"].to(device)

            optimizer.zero_grad()
            outputs = model(images)
            
            loss = sum([loss_func(outputs, poses) for loss_func in loss_functions])

            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
        print(f"Epoch {epoch} loss (mean):", epoch_loss)


if __name__ == "__main__":
    train()