import click
from straymodel.models.straynet import StrayNet
import torch.optim as optim
import torch
import numpy as np
from straymodel.train.objectron.objectron_loss import BoundingBoxLoss
import os
from straymodel.train.objectron.utils import *
from straymodel.utils.visualization_utils import render_example
from tfrecord.torch.dataset import TFRecordDataset
from tfrecord import iterator_utils
import warnings
import pytorch_lightning as pl

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
        images, heatmaps, corner_maps, intrinsics, sizes = batch
        p_heatmaps, _, p_corners = self(images)
        heatmap_loss, corner_loss = self.loss_function(p_heatmaps, p_corners, heatmaps, corner_maps)
        loss = heatmap_loss + corner_loss
        self.log('train_loss', loss)
        self.log('train_heatmap_loss', heatmap_loss)
        self.log('train_corner_loss', corner_loss)
        return loss

    def validation_step(self, batch, batch_idx):
        images, heatmaps, corner_maps, intrinsics, sizes = batch
        p_heatmaps, _, p_corners = self(images)
        heatmap_loss, corner_loss = self.loss_function(p_heatmaps, p_corners, heatmaps, corner_maps)
        loss = heatmap_loss + corner_loss
        self.log('val_loss', loss)
        self.log('val_heatmap_loss', heatmap_loss)
        self.log('val_corner_loss', corner_loss)
        if batch_idx == 0:
            index = np.random.randint(0, p_heatmaps.shape[0])
            heatmap = torch.sigmoid(p_heatmaps[index])
            image = images[index]
            corner_image = render_example(images[index].cpu().numpy(), torch.sigmoid(p_heatmaps[index]).detach().cpu().numpy(),
                    p_corners[index].detach().cpu().numpy(), intrinsics[index].detach().cpu().numpy(), sizes[index].detach().cpu().numpy())
            self.logger.experiment.add_image('image', (image * 255.0).cpu().to(torch.uint8), 0)
            self.logger.experiment.add_image('p_heatmap', heatmap, 0)
            corner_image = np.transpose(corner_image, [2, 0, 1])
            self.logger.experiment.add_image('p_corners', corner_image, 0)
        return loss

    def configure_optimizers(self):
        return optim.Adam(self.model.parameters(), lr=self.lr)

class ObjectronData(pl.LightningDataModule):
    def __init__(self, objectron_dir, batch_size, num_workers):
        super().__init__()
        self.objectron_dir = objectron_dir
        self.batch_size = batch_size
        self.num_workers = num_workers

    def prepare_data(self):
        ensure_index(self.objectron_dir)

    def train_dataloader(self):
        files = [f for f in os.listdir(self.objectron_dir) if '.txt' not in f and 'train' in f]
        blank_corner_map, blank_heatmap = get_blank_maps()

        datasets = (TFRecordDataset(os.path.join(self.objectron_dir, f),
            os.path.join(tmp_dir, index_pattern.format(f))) for f in files)
        dataset = ShufflePool(torch.utils.data.ChainDataset(datasets), 1024)

        def is_valid(xy):
            return xy[0]

        def get_record(xy):
            return xy[1]

        dataset = (dataset
                .map(unpack_record(blank_corner_map, blank_heatmap))
                .filter(is_valid)
                .map(get_record))
        return torch.utils.data.DataLoader(dataset,
                    num_workers=self.num_workers,
                    batch_size=self.batch_size,
                    pin_memory=torch.cuda.is_available())

    def val_dataloader(self):
        files = [f for f in os.listdir(self.objectron_dir) if '.txt' not in f and 'test' in f]
        blank_corner_map, blank_heatmap = get_blank_maps()
        datasets = (TFRecordDataset(os.path.join(self.objectron_dir, f),
            os.path.join(tmp_dir, index_pattern.format(f))) for f in files)
        dataset = torch.utils.data.ChainDataset(datasets)

        def is_valid(xy):
            return xy[0]

        def get_record(xy):
            return xy[1]

        dataset = (dataset
                .map(unpack_record(blank_corner_map, blank_heatmap))
                .filter(is_valid)
                .map(get_record))
        return torch.utils.data.DataLoader(dataset,
                    num_workers=self.num_workers,
                    batch_size=self.batch_size * 2,
                    pin_memory=torch.cuda.is_available())


@click.command()
@click.argument('tfdata', nargs=1)
@click.option('--batch-size', type=int, default=2)
@click.option('--progress-save-folder', default="~/lightning")
@click.option('--num-workers', type=int, default=1)
@click.option('--num-epochs', type=int, default=1)
@click.option('--heatmap-loss-coef', type=float, default=1.0)
@click.option('--corner-loss-coef', type=float, default=1.0)
@click.option('--lr', type=float, default=1e-3)
@click.option('--fp16', is_flag=True)
@click.option('--tune', is_flag=True)
@click.option('--restore', type=str)
def train(tfdata, batch_size, progress_save_folder, num_workers, num_epochs,
        heatmap_loss_coef, corner_loss_coef, lr, fp16, tune,
        restore):
    if restore:
        model = Objectron.load_from_checkpoint(restore,
                heatmap_loss_coef=heatmap_loss_coef,
                corner_loss_coef=corner_loss_coef,
                lr=lr)
    else:
        model = Objectron(heatmap_loss_coef, corner_loss_coef, lr)

    if torch.cuda.is_available():
        gpus = 1
    else:
        gpus = None

    config = {
        'gpus': gpus,
        'accumulate_grad_batches': {
            0: 1,
            num_epochs // 4: 2,
            num_epochs // 2: 4
        },
        'max_epochs': num_epochs
    }
    if fp16:
        config['precision'] = 16

    train = pl.Trainer(**config)

    datamodule = ObjectronData(tfdata, batch_size=batch_size, num_workers=num_workers)

    if tune:
        train.tune(model, datamodule=datamodule)

    train.fit(model, datamodule=datamodule)

if __name__ == "__main__":
    train()
