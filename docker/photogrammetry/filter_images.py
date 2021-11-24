import click
import os
import shutil

@click.command()
@click.argument('scenes', nargs=-1)
@click.option('--every', default=60)
def main(scenes, every):
    for scene in scenes:
        color_path = os.path.join(scene, "color")
        filtered_color_path = os.path.join(scene, "filtered_color")
        os.makedirs(filtered_color_path, exist_ok=True)
        for i, image_path in enumerate(sorted(os.listdir(color_path))):
            if i % every == 0:
                source = os.path.join(color_path, image_path)
                dest = os.path.join(filtered_color_path, image_path)
                shutil.copy(source, dest)


if __name__ == "__main__":
    main()
