import click
from straymodel.models.straynet import StrayNet
import torch.optim as optim
import torch
import numpy as np
from straymodel.train.objectron.objectron_loss import BoundingBoxLoss
import os
from straymodel.train.objectron.utils import *
from tfrecord.torch.dataset import TFRecordDataset
from tfrecord import iterator_utils
import warnings

tmp_dir = "/tmp/bbox3d_train"
tf_record_pattern = "{}"
index_pattern = "{}.index"

class ShufflePool(torch.utils.data.IterableDataset):
    def __init__(self, dataset, pool_size):
        self.dataset = dataset
        self.pool_size = pool_size

    def __iter__(self):
        iterator = iter(self.dataset)
        pool = []
        try:
            for _ in range(self.pool_size):
                pool.append(next(iterator))
        except StopIteration:
            warnings.warn(f"There are less examples than the pool size {self.pool_size}")
        while len(pool) > 0:
            index = np.random.randint(len(pool))
            try:
                item = pool[index]
                pool[index] = next(iterator)
                yield item
            except StopIteration:
                yield pool.pop(index)



def create_dataset(tfrecord_directory):
    files = [f for f in os.listdir(tfrecord_directory) if '.txt' not in f]
    blank_corner_map, blank_heatmap = get_blank_maps()
    splits = {}
    for path in files:
        splits[path] = 1.0 / float(len(files))

    indices = os.path.join(tmp_dir, index_pattern)
    datasets = (TFRecordDataset(os.path.join(tfrecord_directory, f),
        os.path.join(tmp_dir, index_pattern.format(f))) for f in files)
    dataset = ShufflePool(torch.utils.data.ChainDataset(datasets), 1024)

    def is_valid(xy):
        return xy[0]

    def get_record(xy):
        return xy[1]

    return (dataset
            .map(unpack_record(blank_corner_map, blank_heatmap))
            .filter(is_valid)
            .map(get_record)
            )

def ensure_index(tfdata_path):
    os.makedirs(tmp_dir, exist_ok=True)
    from tfrecord.tools import tfrecord2idx
    for filename in sorted(os.listdir(tfdata_path)):
        if ".txt" in filename:
            continue
        path = os.path.join(tfdata_path, filename)
        index_file = os.path.join(tmp_dir, index_pattern.format(filename))
        if not os.path.exists(index_file):
            print(f"Creating index for {filename}")
            tfrecord2idx.create_index(path, os.path.join(tmp_dir, filename + '.index'))

@click.command()
@click.argument('tfdata', nargs=1)
@click.option('--batch-size', type=int, default=2)
@click.option('--progress-save-folder', default="./")
@click.option('--num-workers', type=int, default=1)
@click.option('--num-epochs', type=int, default=1)
@click.option('--heatmap-loss-coef', type=float, default=1.0)
@click.option('--corner-loss-coef', type=float, default=1.0)
@click.option('--lr', type=float, default=1e-3)
def train(tfdata, batch_size, progress_save_folder, num_workers, num_epochs,
        heatmap_loss_coef, corner_loss_coef, lr):
    ensure_index(tfdata)

    os.makedirs(progress_save_folder, exist_ok=True)

    model = StrayNet()

    #TODO: set device globally
    if torch.cuda.is_available():
        device = "cuda:0"
    else:
        device = "cpu"
    model.to(device)

    loss_function = BoundingBoxLoss(heatmap_loss_coef, corner_loss_coef)
    optimizer = optim.Adam(model.parameters(), lr=lr)

    for epoch in range(num_epochs):
        print(f"Epoch {epoch}")
        dataset = create_dataset(tfdata)
        dataloader = torch.utils.data.DataLoader(dataset,
                batch_size=batch_size,
                num_workers=num_workers,
                pin_memory=device=='cuda:0')
        for i, batch in enumerate(dataloader):
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
                save_objectron_sample(epoch_folder, images.cpu().numpy(), torch.sigmoid(p_heatmaps).detach().cpu().numpy(), p_corners.detach().cpu().numpy(), intrinsics, sizes)
                #Don't train on this single batch
                continue

            heatmap_loss, corner_loss = loss_function(p_heatmaps, p_corners, heatmaps, corner_maps)
            loss = heatmap_loss + corner_loss
            loss.backward()
            optimizer.step()
            print(f"Batch {i} heatmap: {heatmap_loss.item():.04f} corner: {corner_loss.item():.04f}", end='\r')
        print("")

        #Saves model every epoch
        script_model = torch.jit.script(model)
        torch.jit.save(script_model, os.path.join(epoch_folder, "model.pt"))



if __name__ == "__main__":
    train()
