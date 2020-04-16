#!/bin/bash
#
# This is a utility script allows you to build the image defined in the current
# directory.

dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
dir_project_root="$(dirname $(dirname ${dir_here}))"

repo_name=$(cat ${dir_here}/config.json | jq '.repo_name' -r) # identifier without aws account info

docker build  --tag "${repo_name}" --file "${dir_here}/Dockerfile" "${dir_project_root}"
#docker image ls # list recently built image
#docker image rm "${repo_name}" # remove recently built image



