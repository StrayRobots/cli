import pytorch_lightning as pl
from tfrecord.torch.dataset import TFRecordDataset
import torch
import os
from straymodel.utils.train_utils import get_blank_maps, unpack_record
from straymodel.data.shuffle_pool import ShufflePool


tmp_dir = "/tmp/bbox3d_train"
tf_record_pattern = "{}"
index_pattern = "{}.index"

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

class ObjectronData(pl.LightningDataModule):
    def __init__(self, objectron_dir, batch_size, num_workers):
        super().__init__()
        self.objectron_dir = objectron_dir
        self.batch_size = batch_size
        self.num_workers = num_workers

    def prepare_data(self):
        ensure_index(self.objectron_dir)

    def train_dataloader(self):
        files = [f for f in os.listdir(self.objectron_dir) if '.txt' not in f and 'train' in f][:20]
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
        files = [f for f in os.listdir(self.objectron_dir)][:3]
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

