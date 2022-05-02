#!/bin/bash

get_platform() {
  echo "$(uname | tr '[:upper:]' '[:lower:]')"
}

version="0.0.2"
arch="$(uname -m)"
tmp_dir="$(mktemp -d)"
install_dir="$HOME/.stray"
platform="$(get_platform)"
endpoint="https://stray-builds.ams3.digitaloceanspaces.com"

download() {
  curl --proto '=https' --tlsv1.2 --show-error --fail --location "$1" --output "$2"
}

install_studio() {
  install_dir=$1
  download "$endpoint/studio/$platform/$arch/latest/studio.tar.gz" "studio.tar.gz"
  tar -xf studio.tar.gz
  folder_name="$(echo Studio-*)"
  mv "$folder_name" studio
  cp studio/bin/studio $install_dir/bin/
  cp studio/bin/preview $install_dir/bin/stray-preview
  cp -r studio/share/stray "$install_dir/share/stray"
}

install_cli() {
  install_dir=$1
  cp "$script_dir/stray" "$install_dir/bin/stray"
  chmod +x "$install_dir/bin/stray"
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
  elif [ -f "$HOME/.bash_profile" ]; then
    add_to_file_unless_exists "$line" "$HOME/.bash_profile"
  fi
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

  popd > /dev/null

  rm -rf $tmp_dir
}

main

