import os
import argparse
import yaml

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target')
    parser.add_argument('--out')
    return parser.parse_args()

def main():
    flags = read_args()

    with open(flags.target, 'rt') as f:
        target_config = yaml.load(f)

    hand_eye_config = {}
    hand_eye_config['april_tag_number_vertical'] = target_config['tagRows']
    hand_eye_config['april_tag_number_horizontal'] = target_config['tagCols']
    hand_eye_config['april_tag_size_m'] = target_config['tagSize']
    hand_eye_config['april_tag_gap_size_m'] = target_config['tagSize'] * target_config['tagSpacing']
    hand_eye_config['april_tag_number_pixel_boarder'] = 2

    with open(flags.out, 'wt') as f:
        f.write(yaml.dump(hand_eye_config))

if __name__ == "__main__":
    main()

