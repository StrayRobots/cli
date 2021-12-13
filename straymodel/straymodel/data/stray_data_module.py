import pytorch_lightning as pl
from straymodel.data.shuffle_pool import ShufflePool
from straymodel.data.scene_dataset import Stray3DBoundingBoxDetectionDataset, Stray3DBoundingBoxScene
import torch

class SceneData(pl.LightningDataModule):
    def __init__(self, scene_dirs, batch_size, num_workers):
        super().__init__()
        self.scene_dirs = scene_dirs
        self.batch_size = batch_size
        self.num_workers = num_workers

    def train_dataloader(self):
        dataset = Stray3DBoundingBoxDetectionDataset(self.scene_dirs, out_size=(60, 80))
        dataset = ShufflePool(dataset, 1024)

        return torch.utils.data.DataLoader(dataset,
                    num_workers=self.num_workers,
                    batch_size=self.batch_size,
                    pin_memory=torch.cuda.is_available())

    def val_dataloader(self):
        dataset = Stray3DBoundingBoxScene(self.scene_dirs[0], out_size=(60, 80))

        return torch.utils.data.DataLoader(dataset,
                    num_workers=1,
                    batch_size=10,
                    pin_memory=torch.cuda.is_available())


