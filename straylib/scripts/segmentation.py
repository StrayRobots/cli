import argparse
import os
from PIL import Image
from straylib import Scene, Renderer

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene')
    return parser.parse_args()

def main():
    flags = read_args()
    scene = Scene(flags.scene)
    renderer = Renderer(scene)
    folder_name = 'semantic'
    os.makedirs(os.path.join(flags.scene, folder_name), exist_ok=True)
    for i in range(0, len(scene), 1):
        print(f"Processing frame {i:06}", end='\r')
        seg = renderer.render_segmentation(i)
        path = os.path.join(flags.scene, folder_name, f"{i:06}.png")
        image = Image.fromarray(seg*255)
        image.save(path)

if __name__ == "__main__":
    main()

