#!/bin/bash
#
# This is a utility script allows you to build the image defined in the current
# directory.

dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
dir_project_root="$(dirname $(dirname ${dir_here}))"
dir_webapp_dockerfile="${dir_here}"

source ${dir_project_root}/bin/py/python-env.sh

path_get_config_value_script="${dir_project_root}/config/get-config-value"

local_repo_name="$(${bin_python} ${path_get_config_value_script} "ECR_REPO_NAME_WEBAPP")"
app_version="$(${bin_python} ${path_get_config_value_script} "APP_VERSION")"
stage="$(${bin_python} ${path_get_config_value_script} "STAGE")"
tag_name="${app_version}-${stage}"

docker build  --tag "${local_repo_name}:${tag_name}" --file "${dir_webapp_dockerfile}/Dockerfile" "${dir_project_root}"
#docker image ls # list recently built image
#docker image rm "${local_repo_name}:${app_version}" # remove recently built image
