import numpy as np
import os
import cv2
from straylib.scene import cube_indices, cube_vertices
from straymodel.data.dataset import I
from straylib.camera import get_scaled_camera_matrix

def draw_epnp_box(cv_image, corners, camera, size):
    vertices = np.copy(cube_vertices)*size
    _, R, t = cv2.solvePnP(vertices, corners, camera, np.zeros(4), flags=cv2.SOLVEPNP_EPNP)
    T_CO = np.eye(4)
    T_CO[:3, :3] = cv2.Rodrigues(R)[0]
    T_CO[:3, 3] = t.flatten()
    image_points = []
    for vertex in vertices:
        vertex_O = np.ones(4, dtype=np.float32)
        vertex_O[:3] = vertex
        vertex_C = (T_CO @ vertex_O)[:3]
        image_point = cv2.projectPoints(vertex_C, cv2.Rodrigues(I)[0], np.zeros(3), camera, np.zeros(4))[0]
        image_points.append(image_point)

    for corner1, vertex1 in zip(image_points, cube_indices):
            for corner2, vertex2 in zip(image_points, cube_indices):
                if np.linalg.norm(vertex1-vertex2) == 1:
                    p1 = (int(corner1.flatten()[0]), int(corner1.flatten()[1]))
                    p2 = (int(corner2.flatten()[0]), int(corner2.flatten()[1]))
                    cv_image = cv2.line(cv_image, p1, p2, (0, 255, 0), 3)
    return cv_image

def draw_box(cv_image, corners):
    for corner1, vertex1 in zip(corners, cube_indices):
        for corner2, vertex2 in zip(corners, cube_indices):
            if np.linalg.norm(vertex1-vertex2) == 1:
                p1 = (int(corner1.flatten()[0]), int(corner1.flatten()[1]))
                p2 = (int(corner2.flatten()[0]), int(corner2.flatten()[1]))
                cv_image = cv2.line(cv_image, p1, p2, (0, 0, 255), 3)
    return cv_image

def save_example(image, heatmap, corner_map, camera, size, folder, idx):
    _, image_height, image_width = image.shape
    _, map_height, map_width = heatmap.shape
    width_scale = image_width / map_width
    height_scale = image_height / map_height
    camera = get_scaled_camera_matrix(camera, width_scale, height_scale)

    where_support = heatmap[0] > 0.0001 #TODO: a better threshold, softmaxed predicted values are unlikely exactly zero?
    corners = extract_image_corners_from_corner_map(corner_map, where_support, map_width, map_height, width_scale, height_scale)

    #Draw heatmap
    cv_image = np.ascontiguousarray(np.moveaxis(image*255, 0, -1), dtype=np.uint8)
    cv_heatmap = np.moveaxis(heatmap/np.max(heatmap)*255, 0, -1).astype(np.uint8)
    cv_heatmap = cv2.applyColorMap(cv_heatmap, cv2.COLORMAP_JET)
    cv_heatmap = cv2.resize(cv_heatmap, (image_width, image_height))
    cv_image = cv2.addWeighted(cv_image, 0.65, cv_heatmap, 0.35, 0)

    #Draw epnp box
    cv_image = draw_epnp_box(cv_image, corners, camera, size)
    #Draw box directly from corners
    cv_image = draw_box(cv_image, corners)

    cv2.imwrite(os.path.join(folder, f"image_{idx}.png"), cv_image)

def save_dataset_snapshot(dataloader, folder, batches=1):
    for i, batch in enumerate(dataloader):
        if i >= batches:
            break
        batch_folder = os.path.join(folder, f"batch_{i}")
        os.makedirs(batch_folder, exist_ok=True)
        images, heatmaps, corner_maps, cameras, _, sizes = batch

        for j, (image, heatmap, corner_map, camera, size) in enumerate(zip(images, heatmaps, corner_maps, cameras, sizes)):
            save_example(image.numpy(), heatmap.numpy(), corner_map.numpy(), camera.numpy(), size.numpy(), batch_folder, j)


def extract_image_corners_from_corner_map(corner_map, where_support, map_width, map_height, width_scale, height_scale):
    corners = []
    x_range = np.arange(map_width)
    y_range = np.arange(map_height)

    corner_map_x = np.tile(x_range, (map_height, 1))
    corner_map_y = np.tile(y_range, (map_width, 1)).T

    if np.sum(where_support) == 0:
        return np.zeros((8,2), dtype=np.float32)

    for i in range(8):
        x_map = corner_map[i*2] + corner_map_x
        y_map = corner_map[i*2 +1] + corner_map_y
        #Average corner predictions based on predicted heats
        corners.append((int(x_map[where_support].mean()*width_scale), int(y_map[where_support].mean()*height_scale)))
    return np.array(corners, dtype=np.float32)