import click
import torch
from straymodel.utils.train_utils import *
import pytorch_lightning as pl
from straymodel.data.objectron_data_module import ObjectronData
from pytorch_lightning.callbacks import ModelCheckpoint
from straymodel.objectron.objectron import Objectron

@click.command()
@click.option('--tfdata', default=None)
@click.option('--batch-size', type=int, default=2)
@click.option('--num-workers', type=int, default=1)
@click.option('--num-epochs', type=int, default=1)
@click.option('--heatmap-loss-coef', type=float, default=1.0)
@click.option('--corner-loss-coef', type=float, default=1.0)
@click.option('--lr', type=float, default=1e-3)
@click.option('--fp16', is_flag=True)
@click.option('--tune', is_flag=True)
@click.option('--restore', type=str)
def train(tfdata, batch_size, num_workers, num_epochs,
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

    checkpoint_callback = ModelCheckpoint(
        monitor="val_loss",
        filename="objectron-{epoch:02d}-{val_loss:.2f}",
        save_top_k=10,
        mode="min",
    )

    train = pl.Trainer(**config, callbacks=[checkpoint_callback])
    datamodule = ObjectronData(tfdata, batch_size=batch_size, num_workers=num_workers)

    if tune:
        train.tune(model, datamodule=datamodule)

    train.fit(model, datamodule=datamodule)

if __name__ == "__main__":
    train()
