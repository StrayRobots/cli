import click
from straymodel.models.straynet import StrayNet
import torch.optim as optim
import torch
from straymodel.train.objectron.objectron_loss import BoundingBoxLoss, spatial_softmax
import os
from straymodel.train.objectron.utils import *
from tfrecord.torch.dataset import TFRecordDataset

def create_dataset(files):
    blank_corner_map, blank_heatmap = get_blank_maps()
    return (TFRecordDataset(files[0], None)
            .map(unpack_record(blank_corner_map, blank_heatmap))
            .filter(lambda xy: xy[0])
            .map(lambda xy: xy[1])
            )

@click.command()
@click.argument('tfdata', nargs=1)
@click.option('--batch-size', type=int, default=2)
@click.option('--progress-save-folder', default="./")
@click.option('--num-workers', type=int, default=1)
@click.option('--num-epochs', type=int, default=1)
@click.option('--heatmap-loss-coef', type=float, default=1.0)
@click.option('--corner-loss-coef', type=float, default=1.0)
def train(tfdata, batch_size, progress_save_folder, num_workers, num_epochs, heatmap_loss_coef, corner_loss_coef):

    os.makedirs(progress_save_folder, exist_ok=True)

    model = StrayNet()

    #TODO: set device globally
    if torch.cuda.is_available():
        device = "cuda:0"
    else:
        device = "cpu"
    model.to(device)

    loss_function = BoundingBoxLoss(heatmap_loss_coef, corner_loss_coef)
    optimizer = optim.Adam(model.parameters())

    files = [os.path.join(tfdata, f) for f in os.listdir(tfdata)]
    for epoch in range(num_epochs):
        print(f"Epoch {epoch}")
        dataset = create_dataset(files)
        dataloader = torch.utils.data.DataLoader(dataset,
                batch_size=batch_size,
                num_workers=num_workers,
                pin_memory=True)
        for i, batch in enumerate(dataloader):
            print(f"Batch {i}", end='\r')
            optimizer.zero_grad()

            images, heatmaps, corner_maps, intrinsics, sizes = batch

            if i == 0 and epoch == 0:
                sample_folder = os.path.join(progress_save_folder, "sample")
                os.makedirs(sample_folder, exist_ok=True)
                save_objectron_sample(sample_folder, images.numpy(), heatmaps.numpy(), corner_maps.numpy(), intrinsics, sizes)

            images = images.to(device)
            heatmaps = heatmaps.to(device)
            corner_maps = corner_maps.to(device)
            p_heatmaps, _, p_corners = model(images)

            if i == 0:
                epoch_folder = os.path.join(progress_save_folder, f"epoch_{epoch}")
                os.makedirs(epoch_folder, exist_ok=True)
                save_objectron_sample(epoch_folder, images.cpu().numpy(), spatial_softmax(p_heatmaps).detach().cpu().numpy(), p_corners.detach().cpu().numpy(), intrinsics, sizes)
                #Don't train on this single batch
                continue

            heatmap_loss, corner_loss = loss_function(p_heatmaps, p_corners, heatmaps, corner_maps)
            loss = heatmap_loss + corner_loss
            loss.backward()
            optimizer.step()

        #Saves model every epoch
        script_model = torch.jit.script(model)
        torch.jit.save(script_model, os.path.join(epoch_folder, "model.pt"))



if __name__ == "__main__":
    train()
