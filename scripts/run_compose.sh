#!/bin/bash

### launches docker-container on your raspberry pi with all python requirements and an sshd server
### allowing to connect via PyCharm to debug source-code.

set -e

# go to base directory of the repo
script_dir_path=$(dirname "$(realpath $0)")
cd "$script_dir_path/../" || exit



docker build -f docker/dewpointvc/Dockerfile -t dewpointvc .
docker-compose -f docker/compose/dewpointvc/docker-compose.yml up
