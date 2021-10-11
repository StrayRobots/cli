from straymodel.data.dataset import Stray3DBoundingBoxDetectionDataset
import click
from torch.utils.data import DataLoader
import torch
from straymodel.utils.visualization_utils import save_example


def inference(model, scenes, inference_save_path, num_examples, device="cpu"):
    model.to(device)
    model.eval()
    dataset = Stray3DBoundingBoxDetectionDataset(scenes, out_size=(80, 60))
    inference_loader = DataLoader(dataset, batch_size=1, shuffle=True, num_workers=1)
    for i, batch in enumerate(inference_loader):
        images, _, _, cameras, _, sizes = [item.to(device) for item in batch]

        p_heatmaps, _, p_corners = model(images)
    
        if i >= num_examples:
            break

        save_example(images[0].cpu().numpy(), p_heatmaps[0].detach().cpu().numpy(), p_corners[0].detach().cpu().numpy(), cameras[0].cpu().numpy(), sizes[0].cpu().numpy(), inference_save_path, i)


@click.command()
@click.argument('scene', nargs=1)
@click.option('--model-path', required=True, type=str)
@click.option('--inference-save-path', default="./", type=str)
@click.option('--num-examples', default=100, type=int)
def main(scenes, model_path, inference_save_path, num_examples):
    if torch.cuda.is_available():
        device = "cuda:0"
    else:
        device = "cpu"
    model = torch.jit.load(model_path)
    inference(scenes, model, inference_save_path, num_examples, device)




if __name__ == "__main__":
    main()