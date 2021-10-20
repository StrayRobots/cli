import click
from straymodel.models.straynet import StrayNet
import torch.optim as optim
import torch
from straymodel.train.objectron.objectron_loss import BoundingBoxLoss, spatial_softmax
import os
import tensorflow as tf
from straymodel.train.objectron.utils import *



@click.command()
@click.argument('tfdata', nargs=1)
@click.option('--batch-size', type=int, default=2)
@click.option('--progress-save-folder', default="./")
@click.option('--num-workers', type=int, default=1)
@click.option('--num-epochs', type=int, default=1)
@click.option('--heatmap-loss-coef', type=int, default=1)
@click.option('--center-loss-coef', type=int, default=1)
@click.option('--corner-loss-coef', type=int, default=1)
@click.option('--shuffle', is_flag=True)
def train(tfdata, batch_size, progress_save_folder, num_workers, num_epochs, heatmap_loss_coef, center_loss_coef, corner_loss_coef, shuffle):

    os.makedirs(progress_save_folder, exist_ok=True)
    #Disable GPU from tf to avoid OOM
    tf.config.set_visible_devices([], 'GPU')

    model = StrayNet()

    #TODO: set device globally
    if torch.cuda.is_available():
        device = "cuda:0"
    else:
        device = "cpu"
    model.to(device)

    loss_function = BoundingBoxLoss(center_loss_coef, heatmap_loss_coef, corner_loss_coef)
    optimizer = optim.Adam(model.parameters())
    blank_corner_map, blank_heatmap = get_blank_maps()

    for epoch in range(num_epochs):
        for i, file in enumerate(os.listdir(tfdata)):
            dataset = tf.data.TFRecordDataset(os.path.join(tfdata,file), num_parallel_reads=num_workers)
            dataset = dataset.batch(batch_size)
            print(f"Epoch {epoch}, TFRecord file {i} ({file})")
            for j, tf_batch in enumerate(dataset.take_while(lambda x: True)):
                valid_batch, batch = get_batch_from_record(tf_batch, blank_heatmap, blank_corner_map)

                if not valid_batch:
                    continue

                images, heatmaps, corner_maps, intrinsics, sizes = batch

                if i == 0 and j == 0 and epoch == 0:
                    sample_folder = os.path.join(progress_save_folder, "sample")
                    os.makedirs(sample_folder, exist_ok=True)
                    save_objectron_sample(sample_folder, images.numpy(), heatmaps.numpy(), corner_maps.numpy(), intrinsics, sizes)
                    
                optimizer.zero_grad()
                images = images.to(device)
                heatmaps = heatmaps.to(device)
                corner_maps = corner_maps.to(device)
                p_heatmaps, _, p_corners = model(images)

                if i == 0 and j == 0:
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