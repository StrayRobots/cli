#!/bin/sh
data_dir=$1

if [ ! -d "$data_dir" ]; then
    echo "data directory does not exist: $data_dir"
    exit 1
fi

docker run -it -v $data_dir:/home/user/data integrate

