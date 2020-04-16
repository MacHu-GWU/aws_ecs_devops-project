#!/bin/bash
#
# This is a utility script allows you to quickly run a
# newly built image and enter it for development or debugging


dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
repo_name=$(cat ${dir_here}/config.json | jq '.repo_name' -r) # identifier without aws account info
container_name="${repo_name}-dev"

docker run --rm -dt --name "${container_name}" -p 10001:80 "${repo_name}"

echo "run this command to enter the container:"
echo
echo "docker exec -it ${container_name} sh"

echo "run this command to delete the container:"
echo
echo "docker container stop ${container_name}"