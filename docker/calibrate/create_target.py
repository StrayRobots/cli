import argparse
import yaml
import subprocess

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target')
    return parser.parse_args()

def main():
    flags = read_args()

    with open(flags.target, 'rt') as f:
        target = yaml.load(f)
    nx = target['tagCols']
    ny = target['tagRows']
    tsize = target['tagSize']
    tspace = target['tagSpacing']
    target_type = target['target_type']
    tag_type = target_type
    if target_type.lower() == 'aprilgrid':
        tag_type = 'apriltag'

    run = ['kalibr_create_target_pdf',
        '--type', tag_type,
        '--nx', str(nx),
        '--ny', str(ny),
        '--tsize', str(tsize),
        '--tspace', str(tspace)]
    subprocess.call(run)

if __name__ == "__main__":
    main()

