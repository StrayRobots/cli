from straymodel.data.dataset import Stray3DBoundingBoxDetectionDataset
import click
from torch.utils.data import DataLoader
import torch
from straymodel.utils.visualization_utils import save_example
from straymodel.train.loss import spatial_softmax
import os


def inference(scene, model, device="cpu"):
    model.to(device)
    model.eval()
    dataset = Stray3DBoundingBoxDetectionDataset([scene], out_size=(80, 60))
    inference_loader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=1)
    inference_save_path = os.path.join(scene, "3d_labeled_examples")
    os.makedirs(inference_save_path, exist_ok=True)
    for i, batch in enumerate(inference_loader):
        images, _, _, cameras, _, sizes = [item.to(device) for item in batch]

        p_heatmaps, _, p_corners = model(images)

        save_example(images[0].cpu().numpy(), spatial_softmax(p_heatmaps)[0].detach().cpu().numpy(), p_corners[0].detach().cpu().numpy(), cameras[0].cpu().numpy(), sizes[0].cpu().numpy(), inference_save_path, i)


@click.command()
@click.argument('scene', nargs=1)
@click.option('--model-path', required=True, type=str)
def main(scene, model_path):
    if torch.cuda.is_available():
        device = "cuda:0"
    else:
        device = "cpu"
    model = torch.jit.load(model_path)
    inference(scene, model, device)




if __name__ == "__main__":
    main()