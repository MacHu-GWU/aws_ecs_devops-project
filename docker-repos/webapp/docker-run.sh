#!/bin/bash
#
# This is a utility script allows you to quickly run a
# newly built image and enter it for development or debugging

dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
dir_project_root="$(dirname $(dirname ${dir_here}))"
dir_webapp_dockerfile="${dir_here}"

source ${dir_project_root}/bin/py/python-env.sh

path_get_config_value_script="${dir_project_root}/config/get-config-value"
local_repo_name="$(${bin_python} ${path_get_config_value_script} "ECR_REPO_NAME_WEBAPP")"
app_version="$(${bin_python} ${path_get_config_value_script} "APP_VERSION")"

container_name="${local_repo_name}-dev"

docker run --rm -dt --name "${container_name}" -p 10001:80 "${local_repo_name}:${app_version}"

echo "run this command to enter the container:"
echo
echo "docker exec -it ${container_name} sh"

echo "run this command to delete the container:"
echo
echo "docker container stop ${container_name}"