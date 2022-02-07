import numpy as np
import struct
from scipy.spatial.transform import Rotation

def read_bytes(file_handle, count, format_sequence, endian_character="<"):
    data = file_handle.read(count)
    return struct.unpack(endian_character + format_sequence, data)

def read_images_bin(path):
    images = []
    with open(path, "rb") as f:
        image_count = read_bytes(f, 8, "Q")[0]
        for _ in range(image_count):
            binary_image_properties = read_bytes(f, 64, "idddddddi")
            image_id = binary_image_properties[0]
            qvec = np.array(binary_image_properties[1:5])
            tvec = np.array(binary_image_properties[5:8])
            image_name = ""
            current_char = read_bytes(f, 1, "c")[0]
            while current_char != b"\x00":
                image_name += current_char.decode("utf-8")
                current_char = read_bytes(f, 1, "c")[0]
            # points 2d count
            num_points_2d = read_bytes(f, 8, "Q")[0]
            # ids
            _ = read_bytes(f, 24 * num_points_2d, "ddq" * num_points_2d)
            T_WC = np.eye(4)
            R = Rotation.from_quat([qvec[1], qvec[2], qvec[3], qvec[0]]).as_matrix()
            T_WC[:3, :3] = R.T
            T_WC[:3, 3] = -R.T @ tvec

            images.append({
                'image_id': image_id,
                'image_filename': image_name,
                'T_WC': T_WC
            })
    return images

