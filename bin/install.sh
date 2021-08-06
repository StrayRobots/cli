#!/bin/bash

get_platform() {
  echo "$(uname | tr '[:upper:]' '[:lower:]')"
}

version="0.0.1"
arch="$(uname -m)"
tmp_dir="$(mktemp -d)"
install_dir="$HOME/.stray"
platform="$(get_platform)"
endpoint="https://stray-builds.ams3.digitaloceanspaces.com"

download() {
  curl --proto '=https' --silent --tlsv1.2 --show-error --fail --location "$1" --output "$2"
}

install_studio() {
  install_dir=$1
  download "$endpoint/studio/$platform/$arch/latest/studio.tar.gz" "studio.tar.gz"
  tar -xf studio.tar.gz
  folder_name="$(echo Studio-*)"
  mv "$folder_name" studio
  cp studio/bin/studio $install_dir/bin/
  cp -r studio/share/stray "$install_dir/share/stray"
}

install_cli() {
  install_dir=$1
  download "$endpoint/cli/stray" "$install_dir/bin/stray"
}

pad() {
  echo ""
  echo $@
  echo ""
}

add_to_file_unless_exists() {
  line=$1
  file=$2
  grep -qxF "$line" $file || pad $line >> $file
}

add_to_path() {
  line="export PATH=$HOME/.stray/bin:\$PATH"
  if [ -f "$HOME/.zshrc" ]; then
    add_to_file_unless_exists "$line" "$HOME/.zshrc"
  fi
  if [ -f "$HOME/.bashrc" ]; then
    add_to_file_unless_exists "$line" "$HOME/.bashrc"
  fi
}

install_python_env() {
  download "$endpoint/cli/$platform/$arch/latest/install_env.sh" "install_env.sh"
  chmod +x install_env.sh
  ./install_env.sh -bu -p $HOME/.stray/env

  source "$HOME/.stray/env/bin/activate"
  model_wheel_name="straymodel-$version-py38-none-any.whl"
  lib_wheel_name="straylib-$version-py38-none-any.whl"
  label_wheel_name="straylabel-$version-py38-none-any.whl"
  echo "$lib_wheel_name"
  download "$endpoint/straymodel/$model_wheel_name" "$model_wheel_name"
  download "$endpoint/straylib/$lib_wheel_name" "$lib_wheel_name"
  download "$endpoint/straylabel/$label_wheel_name" "$label_wheel_name"
  pip install $lib_wheel_name $model_wheel_name $label_wheel_name
}

main() {
  set -e
  mkdir -p "$install_dir/bin"
  mkdir -p "$install_dir/share"
  mkdir -p "$install_dir/include"
  mkdir -p "$install_dir/lib"

  pushd $tmp_dir > /dev/null

  echo "Installing Stray Studio."
  install_studio $install_dir
  echo "Installing CLI."
  install_cli $install_dir
  add_to_path
  echo "Installing Python environment."
  install_python_env

  popd > /dev/null

  rm -rf $tmp_dir
}

main

