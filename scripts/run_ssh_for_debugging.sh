#!/bin/bash

set -e

# go to base directory of the repo
script_dir_path=$(dirname "$(realpath $0)")
cd "$script_dir_path/../" || exit




if [ -d tmp/dev_ssh_hostkeys/ ]; then
  echo "keys found in tmp/dev_ssh_hostkeys/, skipping generating them"
else
  echo "generating host-keys"
  mkdir -p tmp/dev_ssh_hostkeys/etc/ssh
  ssh-keygen -A -f tmp/dev_ssh_hostkeys/
fi


docker build -f docker/dev_ssh/Dockerfile -t dewpointvc_devssh .
docker run --rm -it --device /dev/gpiomem -p 1022:22 --entrypoint sh dewpointvc_devssh
