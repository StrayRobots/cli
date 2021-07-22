import os
from PIL import Image
from straylib import Scene, Renderer


def segment(scene_path):
    scene = Scene(scene_path)
    renderer = Renderer(scene)
    semantic_path = os.path.join(scene_path, "semantic")
    os.makedirs(semantic_path, exist_ok=True)
    for i in range(0, len(scene), 1):
        print(f"Processing frame {i:06}", end='\r')
        seg = renderer.render_segmentation(i)
        path = os.path.join(semantic_path, f"{i:06}.png")
        image = Image.fromarray(seg)
        image.save(path)
    print(f"Saved segmetations to {semantic_path}")


