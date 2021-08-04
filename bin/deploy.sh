#!/bin/bash


main() {
  source_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
  destination="s3://stray-builds/cli/stray"
  s3cmd put "$source_dir/stray" $destination
  s3cmd setacl $destination --acl-public
}

main

