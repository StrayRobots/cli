import click
import os
import torch
import cv2
from train_objectron import Objectron, ObjectronData
from straymodel.utils.visualization_utils import render_example

@click.command()
@click.argument('checkpoint')
@click.option('--data', type=str, required=True)
@click.option('--batch-size', default=1)
@click.option('--out', default='/tmp/samples')
def main(checkpoint, data, **kwargs):
    model = Objectron.load_from_checkpoint(checkpoint).model
    model.eval()

    data = ObjectronData(data, batch_size=1, num_workers=4)

    os.makedirs(kwargs['out'], exist_ok=True)
    with torch.autograd.inference_mode():
        test_loader = data.val_dataloader()
        i = 0
        for batch in test_loader:
            images, _, _, intrinsics, sizes = batch
            p_heatmaps, _, p_corners = model(images)

            p_heatmaps = torch.sigmoid(p_heatmaps).cpu().numpy()
            p_corners = p_corners.cpu().numpy()
            intrinsics = intrinsics.cpu().numpy()
            sizes = sizes.cpu().numpy()
            images = images.cpu().numpy()
            for (p_heatmap, p_corners,
                    intrinsic, size, image) in zip(p_heatmaps, p_corners, intrinsics, sizes, images):

                corner_image = render_example(image, p_heatmap,
                        p_corners, intrinsic, size)

                print(f"Saving image {i:06}")
                cv2.imwrite(os.path.join(kwargs['out'], f"sample_{i:06}.webp"), corner_image)
                i += 1



if __name__ == "__main__":
    main()
