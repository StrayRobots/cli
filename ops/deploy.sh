#!/bin/bash

arch="$(uname -m)"
platform="$(uname | tr '[:upper:]' '[:lower:]')"
s3_bucket="s3://stray-builds"
ops_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source_dir="$(dirname $ops_dir)"

upload_public() {
  file=$1
  destination=$2
  s3cmd put $file $destination
  s3cmd setacl $destination --acl-public
}

deploy_python_env() {
  pushd "$ops_dir/package" > /dev/null

  constructor .
  upload_public "install_env.sh" "$s3_bucket/cli/$platform/$arch/latest/install_env.sh"
  rm install_env.sh

  popd > /dev/null
}

make_wheel() {
  $HOME/.stray/env/bin/python setup.py bdist_egg --exclude-source-files
  wheel convert dist/*
}

deploy_wheels() {
  pushd "$source_dir/model/" > /dev/null
  make_wheel
  wheel_file="$(basename $(find straymodel-*))"
  echo "wheel: $wheel_file uploading to $s3_bucket/straymodel/$wheel_file"
  upload_public "$wheel_file" "$s3_bucket/straymodel/$wheel_file"

  popd > /dev/null
  pushd "$source_dir/label/" > /dev/null
  make_wheel
  wheel_file="$(basename $(find straylabel-*))"
  upload_public "$wheel_file" "$s3_bucket/straylabel/$wheel_file"
  popd > /dev/null

  pushd "$source_dir/straylib/" > /dev/null
  make_wheel
  wheel_file="$(basename $(find straylib-*))"
  upload_public "$wheel_file" "$s3_bucket/straylabel/$wheel_file"
  popd
}

main() {
  set -e

  upload_public "$source_dir/bin/stray" "$s3_bucket/cli/stray"
  upload_public "$source_dir/bin/install.sh" "$s3_bucket/cli/install.sh"

  deploy_python_env
  deploy_wheels
}

main

