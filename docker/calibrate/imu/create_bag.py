import argparse
import subprocess
import csv

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-csv', default="/home/workspace/data/imu.csv")
    parser.add_argument('--out-csv', default="/tmp/imu.csv")
    return parser.parse_args()

def to_ns(ts_string):
    return int(float(ts_string) * 1e9)

def convert_imu(in_csv, out_csv):
    with open(in_csv, 'rt') as f:
        reader = csv.reader(f)
        next(reader)
        with open(out_csv, 'wt') as f_out:
            writer = csv.writer(f_out)
            writer.writerow(['timestamp ns', 'rotation x', 'rotation y', 'rotation z', 'acc x', 'acc y', 'acc z'])
            for line in reader:
                writer.writerow([to_ns(line[0])] + line[4:] + line[1:4])

def main():
    flags = read_args()

    convert_imu(flags.in_csv, flags.out_csv)

if __name__ == "__main__":
    main()

